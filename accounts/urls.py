from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .views import LoginView, RegisterView, VerifyEmailView, EmailVerificationCompleteView, VerifyPhoneView, \
    PhoneVerificationCompleteView, ChangeEmailView, PhoneUpdateView, \
    ResendPhoneConfirmationView, UpdateProfileInfoView

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # email urls
    path('verify/email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('verify/email/complete', EmailVerificationCompleteView.as_view(), name='email-verification-complete'),

    # phone urls
    path('verify/phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('verify/phone/complete', PhoneVerificationCompleteView.as_view(), name='phone-verification-complete'),
    path('resend_phone_activation/', ResendPhoneConfirmationView.as_view(), name='resend_phone_activation'),

    # password urls
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        success_url=reverse_lazy('password_reset_done'),
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt'
    ), name='password_reset'),

    path('password_reset/done', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    path('reset/done', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('email-change/', ChangeEmailView.as_view(), name='email-update'),
    path('phone-change/', PhoneUpdateView.as_view(), name='phone-update'),

    # update profile info
    path('profile/', UpdateProfileInfoView.as_view(), name='update_profile'),

]
