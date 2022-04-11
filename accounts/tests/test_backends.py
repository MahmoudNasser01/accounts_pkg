from django.test import TestCase, override_settings, Client

from accounts.factories import UserFactory


class UsernameOrPhoneModelBackendTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    @override_settings(AUTHENTICATION_BACKENDS=["accounts.backends.UsernameOrPhoneModelBackend"])
    def test_it_logs_user_in_with_user_email(self):
        self.client.login(email=self.user.email, password="secret")
        self.assertIn("sessionid", self.client.cookies)

    @override_settings(AUTHENTICATION_BACKENDS=["accounts.backends.UsernameOrPhoneModelBackend"])
    def test_it_logs_user_in_with_username_field_form_kwargs(self):
        self.client.login(email=self.user.email, password="secret")
        self.assertIn("sessionid", self.client.cookies)

    @override_settings(AUTHENTICATION_BACKENDS=["accounts.backends.UsernameOrPhoneModelBackend"])
    def test_it_logs_user_in_with_username(self):
        self.client.login(username=self.user.email, password="secret")
        self.assertIn("sessionid", self.client.cookies)

    @override_settings(AUTHENTICATION_BACKENDS=["accounts.backends.UsernameOrPhoneModelBackend"])
    def test_it_logs_user_in_with_phone(self):
        self.client.login(phone=self.user.phone, password="secret")
        self.assertIn("sessionid", self.client.cookies)

    @override_settings(AUTHENTICATION_BACKENDS=["accounts.backends.UsernameOrPhoneModelBackend"])
    def test_it_fails_if_username_email_or_phone_are_not_provided(self):
        self.client.login(password="secret")
        self.assertNotIn("sessionid", self.client.cookies)

    @override_settings(AUTHENTICATION_BACKENDS=["accounts.backends.UsernameOrPhoneModelBackend"])
    def test_it_fails_if_password_is_not_provided(self):
        self.client.login(email=self.user.email)
        self.assertNotIn("sessionid", self.client.cookies)

    @override_settings(AUTHENTICATION_BACKENDS=["accounts.backends.UsernameOrPhoneModelBackend"])
    def test_it_fails_if_password_is_not_correct(self):
        self.client.login(email=self.user.email, password="lol")
        self.assertNotIn("sessionid", self.client.cookies)

    @override_settings(AUTHENTICATION_BACKENDS=["accounts.backends.UsernameOrPhoneModelBackend"])
    def test_it_fails_if_user_is_not_active(self):
        self.user.is_active = False
        self.user.save()
        self.client.login(email=self.user.email, password="secret")
        self.assertNotIn("sessionid", self.client.cookies)

    @override_settings(AUTHENTICATION_BACKENDS=["accounts.backends.UsernameOrPhoneModelBackend"])
    def test_it_fails_if_user_does_not_exists(self):
        self.client.login(email="doesnotexist@mail.com", password="secret")
        self.assertNotIn("sessionid", self.client.cookies)

