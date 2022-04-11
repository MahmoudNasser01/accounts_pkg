from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views_api import UpdateEmailAPIView, UpdateProfileDataAPIView, UpdatePhoneAPIView, VerifyPhoneAPIView, \
    VerifyEmailAPIView, ResendPhoneConfirmationAPIView, UserSignupAPIView, ResendEmailConfirmationLinkView, \
    UserLogoutAPIView, PasswordResetAPIView

app_name = 'accounts'

urlpatterns = [

    # simple jwt
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', UserLogoutAPIView.as_view(), name='logout'),
    path('signup/', UserSignupAPIView.as_view(), name='signup'),

    # password
    path('password_reset/', PasswordResetAPIView.as_view(), name='password_reset'),

    # email verification
    path('verify/email/<str:uidb64>/<str:token>/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('resend_email_activation/', ResendEmailConfirmationLinkView.as_view(), name='resend-email-activation'),

    # phone verification
    path('verify/phone/', VerifyPhoneAPIView.as_view(), name='verify-phone'),
    path('resend_phone_activation/', ResendPhoneConfirmationAPIView.as_view(), name='resend_phone_activation'),

    # profile urls
    path('update/', UpdateProfileDataAPIView.as_view(), name='profile_info'),
    path('email/update/', UpdateEmailAPIView.as_view(), name='update_email'),
    path('phone/update/', UpdatePhoneAPIView.as_view(), name='update_phone'),
]
