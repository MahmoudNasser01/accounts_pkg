from pyexpat.errors import messages

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _
from django.views import View

from .forms import PhoneLoginForm, UserCreationForm, VerifyPhoneForm
from .forms import UpdatePhoneNumberForm, UpdateEmailForm, UserChangeForm
from .services.activation_email import send_mail_confirmation
from .tokens import account_activation_token
from .verify_phone import VerifyPhone


class UpdateProfileInfoView(LoginRequiredMixin, View):
    def get_form_class(self):
        return getattr(settings, "PROFILE_FORM", UserChangeForm)

    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/update_user_data_form.html', {
            'form': self.get_form_class(),
            "page_title": _("Update User Info")
        })

    def post(self, request, *args, **kwargs):
        form = self.get_form_class()(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('your profile has been updated successfully'))
            return redirect(reverse('site:profile:index'))
        return render(request, 'accounts/update_user_data_form.html', {
            'form': form
        })


class ChangeEmailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/update_email_form.html', {
            'form': UpdateEmailForm(),
            "page_title": _("Update Email")
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        form = UpdateEmailForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'your email has been updated successfully')
            return redirect(reverse('site:profile:index'))

        return render(request, 'accounts/update_email_form.html', {
            'form': form
        })


class PhoneUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/update_phone_number_form.html', {
            'form': UpdatePhoneNumberForm(),
            "page_title": _("Update Phone Number")
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        form = UpdatePhoneNumberForm(user, request.POST)
        if form.is_valid():
            request.user.phone_verified_at = None
            request.user.save()
            return redirect(reverse('site:profile:index'))

        return render(request, 'users/profile/update_phone_number_form.html', {
            "form": form
        })


UserModel = get_user_model()


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_form_class(self):
        if getattr(settings, 'PHONE_AUTHENTICATION_ACTIVE', False):
            return PhoneLoginForm
        return getattr(settings, 'LOGIN_FORM', AuthenticationForm)


class RegisterView(View):
    def get_form_class(self):
        return getattr(settings, "REGISTER_FORM", UserCreationForm)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(request, 'accounts/register.html', {
            "form": self.get_form_class()()
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        form = self.get_form_class()(request.POST)
        if form.is_valid():
            user = form.save()
            login(self.request, user)
            send_mail_confirmation(request, user)
            VerifyPhone().send(user.phone)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect(settings.LOGIN_REDIRECT_URL)

        return render(self.request, 'accounts/register.html', {
            "form": form
        })


# phone verification
class VerifyPhoneView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.phone_verified_at is not None:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return render(request, 'accounts/verify_phone.html', {
            "form": VerifyPhoneForm(user=request.user)
        })

    def post(self, request, *args, **kwargs):
        if request.user.phone_verified_at is not None:
            return redirect(settings.LOGIN_REDIRECT_URL)

        form = VerifyPhoneForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.phone_verified_at = now()
            request.user.save()
            return redirect(reverse("phone-verification-complete"))

        return render(request, 'accounts/verify_phone.html', {"form": form})


class PhoneVerificationCompleteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "accounts/phone_verification_complete.html")


class ResendPhoneConfirmationView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        VerifyPhone().send(request.user.phone)
        messages.success(request, _("A new confirmation code has been sent to your phone"))
        return redirect(reverse("verify-phone"))


# email verification

class VerifyEmailView(LoginRequiredMixin, View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.email_verified_at = now()
            user.save()

        return redirect('email-verification-complete')


class EmailVerificationCompleteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/email_verification_complete.html', {
            'verified': request.user.email_verified_at
        })


class ResendEmailConfirmationLinkView(View):
    def get(self, request, *args, **kwargs):
        send_mail_confirmation(request, request.user)
        messages.success(request, 'email verification is sent successfully')
        return redirect(kwargs['next'])
