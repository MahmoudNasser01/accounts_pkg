from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.forms import UpdateEmailForm, UpdatePhoneNumberForm
from .forms import VerifyPhoneForm
from .serializers import LogoutSerializer, PasswordResetSerializer, UpdateUserDataSerializer, RegisterSerializer
from .services.activation_email import send_mail_confirmation
from .tokens import account_activation_token
from .verify_phone import VerifyPhone

UserModel = get_user_model()


class UserSignupAPIView(APIView):
    access_token = None
    refresh_token = None
    token = None
    user = None
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            self.user = serializer.save()
            send_mail_confirmation(request, self.user)
            VerifyPhone().send(self.user.phone)
            refresh = RefreshToken.for_user(self.user)
            return Response({"access_token": str(refresh.access_token), "refresh_token": str(refresh)},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class UserLogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetAPIView(APIView):
    permission_classes = []
    authentication_classes = []
    email_template_name = 'accounts/password_reset_email.html'
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    subject_template_name = 'accounts/password_reset_subject.txt'
    token_generator = default_token_generator

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            opts = {
                'use_https': self.request.is_secure(),
                'token_generator': self.token_generator,
                'from_email': self.from_email,
                'email_template_name': self.email_template_name,
                'subject_template_name': self.subject_template_name,
                'request': self.request,
                'html_email_template_name': self.html_email_template_name,
                'extra_email_context': self.extra_email_context,
            }
            serializer.save(opts=opts)
            return Response({"message": "{} {}".format(
                _('We’ve emailed you instructions for setting your password, '
                  'if an account exists with the email you entered. You should receive them shortly.'),
                _('If you don’t receive an email, please make sure you’ve entered '
                  'the address you registered with, and check your spam folder.'))},
                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


# phone verification

class VerifyPhoneAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        if request.user.phone_verified_at is not None:
            return Response({'message': 'this account was activated before'}, status=status.HTTP_400_BAD_REQUEST)

        form = VerifyPhoneForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.phone_verified_at = now()
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ResendPhoneConfirmationAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        VerifyPhone().send(request.user.phone)
        return Response({"message": _('Code was resent successfully.')}, status=status.HTTP_200_OK)


# email verification
class ResendEmailConfirmationLinkView(APIView):
    def get(self, request, *args, **kwargs):
        send_mail_confirmation(request, request.user)
        return Response({"message": 'Email activation link resent successfully'})


class VerifyEmailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.email_verified_at = now()
            user.save()
        return Response({"message": _('Email was verified successfully.')}, status=status.HTTP_200_OK)


# user profile
class UpdateProfileDataAPIView(APIView):
    """
    An endpoint for changing User Profile Data.
    """

    def get_serializer_class(self):
        return getattr(settings, "PROFILE_SERIALIZER", UpdateUserDataSerializer)

    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data, instance=request.user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class UpdateEmailAPIView(APIView):
    """
    An endpoint for changing Email.
    """
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        # todo: change this serializer to basic Update Email Form
        return getattr(settings, "UPDATE_EMAIL_FORM", UpdateEmailForm)

    def put(self, request, *args, **kwargs):
        validation_from = self.get_serializer_class()(data=request.data, user=request.user)
        if validation_from.is_valid():
            validation_from.save()
            return Response({'message': _('Email Changed Successfully')}, status=status.HTTP_201_CREATED)
        return Response(validation_from.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class UpdatePhoneAPIView(APIView):
    """
    An endpoint for changing Phone.
    """
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        return getattr(settings, "UPDATE_PHONE_FORM", UpdatePhoneNumberForm)

    def put(self, request, *args, **kwargs):
        validated_fields = self.get_serializer_class()(data=request.data, user=request.user)
        if validated_fields.is_valid():
            validated_fields.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(validated_fields.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
