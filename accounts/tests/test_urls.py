from django.contrib.auth import views
from django.test import TestCase
from django.urls import resolve, reverse

from accounts.views import ResendPhoneConfirmationView, VerifyPhoneView, PhoneVerificationCompleteView, LoginView, \
    RegisterView
from accounts.views_api import UpdateProfileDataAPIView, UpdateEmailAPIView, UpdatePhoneAPIView, VerifyPhoneAPIView, \
    ResendPhoneConfirmationAPIView, VerifyEmailAPIView, ResendEmailConfirmationLinkView


class SiteUrlsTestCase(TestCase):
    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func.view_class, LoginView)

    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func.view_class, RegisterView)

    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func.view_class, views.LogoutView)

    # phone urls
    def test_phone_verify_url_resolves(self):
        url = reverse("verify-phone")
        self.assertEquals(resolve(url).func.view_class, VerifyPhoneView)

    def test_resend_phone_confirmation_url_resolves(self):
        url = reverse("resend_phone_activation")
        self.assertEquals(resolve(url).func.view_class, ResendPhoneConfirmationView)

    def test_phone_verify_complete_url_resolves(self):
        url = reverse("phone-verification-complete")
        self.assertEquals(resolve(url).func.view_class, PhoneVerificationCompleteView)


class APIUrlsTestCase(TestCase):

    # EMAIL
    def test_verify_email_confirmation_url_resolves(self):
        url = reverse('api-v1:accounts:verify-email', args=['token', 'email'])
        self.assertEquals(resolve(url).func.view_class, VerifyEmailAPIView)

    def test_resend_email_confirmation_code_url_resolves(self):
        url = reverse('api-v1:accounts:resend-email-activation')
        self.assertEqual(resolve(url).func.view_class, ResendEmailConfirmationLinkView)

    # phone verification
    def test_phone_verify_url_resolves(self):
        url = reverse("api-v1:accounts:verify-phone")
        self.assertEquals(resolve(url).func.view_class, VerifyPhoneAPIView)

    def test_resend_phone_activation_code_url_resolves(self):
        url = reverse('api-v1:accounts:resend_phone_activation')
        self.assertEqual(resolve(url).func.view_class, ResendPhoneConfirmationAPIView)

    # profile
    def test_user_update_profile_info_api_view_url_resolves(self):
        url = reverse('api-v1:accounts:profile_info')
        self.assertEqual(resolve(url).func.view_class, UpdateProfileDataAPIView)

    def test_update_user_email_api_view_url_resolves(self):
        url = reverse('api-v1:accounts:update_email')
        self.assertEqual(resolve(url).func.view_class, UpdateEmailAPIView)

    def test_update_user_phone_api_view_url_resolves(self):
        url = reverse('api-v1:accounts:update_phone')
        self.assertEqual(resolve(url).func.view_class, UpdatePhoneAPIView)
