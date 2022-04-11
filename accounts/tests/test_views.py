import inspect

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LoginView as BaseLoginView
from django.test import TestCase, Client
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views import View

from ..factories import UserFactory
from ..forms import PhoneLoginForm, RegisterForm, UserCreationForm, UpdateUserDataForm
from ..tokens import account_activation_token
from ..views import LoginView, RegisterView, VerifyPhoneView, PhoneVerificationCompleteView, VerifyEmailView, \
    EmailVerificationCompleteView, UpdateProfileInfoView, PhoneUpdateView, ResendEmailConfirmationLinkView, \
    ResendPhoneConfirmationView

UserModel = get_user_model()


class TestLoginForm(AuthenticationForm):
    pass


class LoginViewStructureTestCase(TestCase):
    def test_it_extends_django_LoginView(self):
        self.assertTrue(issubclass(LoginView, BaseLoginView))

    def test_it_has_template_name(self):
        self.assertIn('template_name', dict(inspect.getmembers(LoginView)))

    def test_template_name_is_authentication_login(self):
        self.assertEquals(LoginView.template_name, 'accounts/login.html')

    def test_it_has_redirect_authenticated_user(self):
        self.assertIn('redirect_authenticated_user', dict(inspect.getmembers(LoginView)))

    def test_redirect_authenticated_user_is_true(self):
        self.assertTrue(LoginView.redirect_authenticated_user)

    def test_it_has_form_class(self):
        self.assertIn('get_form_class', dict(inspect.getmembers(LoginView)))

    def test_get_form_class_is_callable(self):
        self.assertTrue(callable(LoginView.get_form_class))


class LoginViewGetFormClassTestCase(TestCase):
    @override_settings(PHONE_AUTHENTICATION_ACTIVE=False)
    def test_it_returns_default_login_form_if_phone_authentication_active_is_false_and_authentication_form_is_none(
            self):
        self.assertTrue(issubclass(LoginView().get_form_class(), AuthenticationForm))

    @override_settings(PHONE_AUTHENTICATION_ACTIVE=True)
    def test_it_returns_phone_login_form_if_phone_authentication_active_is_true(self):
        self.assertTrue(issubclass(LoginView().get_form_class(), PhoneLoginForm))

    @override_settings(LOGIN_FORM=TestLoginForm)
    def test_it_returns_settings_login_form_if_is_set(self):
        self.assertTrue(issubclass(LoginView().get_form_class(), TestLoginForm))


class LoginViewPOSTTestCase(TestCase):
    def test_it_redirects_to_settings_login_redirect_url_if_user_is_logged_in(self):
        client = Client()
        user = UserFactory()
        client.login(email=user.email, password="secret")
        response = client.post(reverse('login'))
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)


class RegisterViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(RegisterView, View))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(RegisterView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(RegisterView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(RegisterView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(RegisterView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(RegisterView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(RegisterView.post)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_view_has_method_get_form_class(self):
        self.assertTrue(hasattr(RegisterView, 'get_form_class'))

    def test_view_has_method_get_form_class_is_callable(self):
        self.assertTrue(callable(RegisterView.get_form_class))

    def test_get_form_class_method_signature(self):
        expected_signature = ['self']
        actual_signature = inspect.getfullargspec(RegisterView.get_form_class)[0]
        self.assertEquals(actual_signature, expected_signature)


class RegisterViewGetFormClassTestCase(TestCase):
    def test_it_returns_django_user_creation_form_if_settings_register_from_is_not_set(
            self):
        self.assertTrue(issubclass(RegisterView().get_form_class(), UserCreationForm))

    @override_settings(REGISTER_FORM=RegisterForm)
    def test_it_returns_django_user_creation_form_if_settings_register_from_is_set(self):
        self.assertTrue(issubclass(RegisterView().get_form_class(), RegisterForm))


class RegisterViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_it_redirects_to_settings_login_redirect_url_if_user_is_logged_in(self):
        user = UserFactory()
        self.client.login(email=user.email, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_returns_register_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_it_returns_form_in_response_context(self):
        response = self.client.get(self.url)
        self.assertIn('form', response.context)

    @override_settings(REGISTER_FORM=RegisterForm)
    def test_response_context_form_is_instance_of_register_form_if_settings_register_from_is_set(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], RegisterForm)


class RegisterViewPOSTTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')
        self.data = {
            "email": "test@test.test",
            "username": "TestUser",
            # "phone": "+201005263988",
            "password1": "newTESTPasswordD",
            "password2": "newTESTPasswordD",
        }

    def test_it_redirects_to_settings_login_redirect_url_if_user_is_logged_in(self):
        user = UserFactory()
        self.client.login(email=user.email, password="secret")
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_creates_user_with_provided_data(self):
        self.client.post(self.url, self.data)
        self.assertTrue(get_user_model().objects.filter(username="TestUser").exists())

    def test_it_logs_in_the_created_user(self):
        self.client.post(self.url, self.data)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEquals(self.client.session['_auth_user_id'],
                          str(get_user_model().objects.get(username="TestUser").id))

    @override_settings(LOGIN_REDIRECT_URL="/accounts/login/")
    def test_it_redirect_to_next_if_next_in_request(self):
        self.data.update({"next": '/'})
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_it_redirects_to_settings_login_redirect_url_if_next_is_not_provided(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_returns_register_template_if_form_is_invalid(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_it_returns_form_in_response_context_if_form_is_invalid(self):
        response = self.client.post(self.url)
        self.assertIn('form', response.context)

    @override_settings(REGISTER_FORM=RegisterForm)
    def test_response_context_form_is_instance_of_register_form_if_settings_register_from_is_set(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], RegisterForm)


# phone views
class VerifyPhoneViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(VerifyPhoneView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(VerifyPhoneView, LoginRequiredMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(VerifyPhoneView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(VerifyPhoneView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(VerifyPhoneView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(VerifyPhoneView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(VerifyPhoneView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(VerifyPhoneView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyPhoneViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password="secret")
        self.url = reverse('verify-phone')

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url, fetch_redirect_response=False)

    def test_it_redirects_to_settings_login_redirect_url_if_phone_is_verified(self):
        user = UserFactory(phone_verified_at=now())
        self.client.login(email=user.email, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False)

    def test_it_returns_verify_phone_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "accounts/verify_phone.html")

    def test_it_returns_form_in_response_context(self):
        response = self.client.get(self.url)
        self.assertIn('form', response.context)


class VerifyPhoneViewPOSTTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(phone="201002536987")
        self.client.login(email=self.user.email, password="secret")
        self.url = reverse('verify-phone')
        self.data = {"code": "777777"}

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url, fetch_redirect_response=False)

    def test_it_redirects_to_settings_login_redirect_url_if_phone_is_verified(self):
        user = UserFactory(phone_verified_at=now())
        self.client.login(email=user.email, password="secret")
        response = self.client.post(self.url)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

    def test_it_updates_phone_verified_at_column_in_user_model_to_now_on_success(self):
        self.client.post(self.url, self.data)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.phone_verified_at)

    def test_it_redirects_to_phone_verification_complete_on_success(self):
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse("phone-verification-complete"), fetch_redirect_response=False)

    def test_it_returns_verify_phone_template_on_failure(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "accounts/verify_phone.html")

    def test_it_returns_form_in_response_context_on_failure(self):
        response = self.client.post(self.url)
        self.assertIn('form', response.context)


class PhoneVerificationCompleteViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(PhoneVerificationCompleteView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(PhoneVerificationCompleteView, LoginRequiredMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(PhoneVerificationCompleteView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(PhoneVerificationCompleteView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(PhoneVerificationCompleteView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class PhoneVerificationCompleteViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password="secret")
        self.url = reverse('phone-verification-complete')

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

    def test_it_returns_phone_verification_complete_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "accounts/phone_verification_complete.html")


class ResendPhoneConfirmationViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(ResendPhoneConfirmationView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(ResendPhoneConfirmationView, LoginRequiredMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(ResendPhoneConfirmationView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(ResendPhoneConfirmationView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ResendPhoneConfirmationView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class ResendPhoneConfirmationViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password="secret")
        self.url = reverse("resend_phone_activation")

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

    def test_it_redirect_to_phone_verification_again(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("verify-phone"))

    def test_message_is_correct(self):
        response = self.client.get(self.url, follow=True)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(str(msgs[0]), _("A new confirmation code has been sent to your phone"))


# Email Verification


class VerifyEmailViewStructureTestCase(TestCase):

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(VerifyEmailView, LoginRequiredMixin))

    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(VerifyEmailView, View))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(VerifyEmailView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(VerifyEmailView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request', 'uidb64', 'token']
        actual_signature = inspect.getfullargspec(VerifyEmailView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyEmailViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password="secret")
        self.user = User.objects.get(pk=self.user.pk)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)

    def test_it_activate_the_user(self):
        confirm = self.client.get(reverse('verify-email', args=[self.uid, self.token]))
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verified_at)

    def test_it_redirects_to_phone_verification_complete_on_success(self):
        confirm = self.client.get(reverse('verify-email', args=[self.uid, self.token]))
        self.assertRedirects(confirm, reverse('email-verification-complete'))


class EmailVerificationCompleteViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(EmailVerificationCompleteView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(EmailVerificationCompleteView, LoginRequiredMixin))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(EmailVerificationCompleteView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(EmailVerificationCompleteView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(EmailVerificationCompleteView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class EmailVerificationCompleteViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password="secret")
        self.url = reverse('email-verification-complete')

    def test_it_redirects_to_login_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url, fetch_redirect_response=False)

    def test_it_returns_phone_verification_complete_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "accounts/email_verification_complete.html")


class ResendEmailConfirmationLinkViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(ResendEmailConfirmationLinkView, View))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(ResendEmailConfirmationLinkView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(ResendEmailConfirmationLinkView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ResendEmailConfirmationLinkView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


# profile views

class UpdateProfileInfoViewStructureTestCase(TestCase):

    @override_settings(PROFILE_FORM=RegisterForm)
    def setUp(self):
        pass

    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(UpdateProfileInfoView, View))

    def test_it_extends_login_required_mixin(self):
        self.assertTrue(issubclass(UpdateProfileInfoView, LoginRequiredMixin))

    def test_view_has_method_get_form_class(self):
        self.assertTrue(hasattr(UpdateProfileInfoView, 'get_form_class'))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(UpdateProfileInfoView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(UpdateProfileInfoView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UpdateProfileInfoView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(UpdateProfileInfoView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(UpdateProfileInfoView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UpdateProfileInfoView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class UpdateProfileInfoGetViewTestCase(TestCase):

    @override_settings(PROFILE_FORM=UpdateUserDataForm)
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(email=self.user.email, password='secret')
        self.url = reverse('site:profile:profile-update')

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "users/profile/update_user_data_form.html")

    def test_context_contains_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_context_contains_page_title(self):
        response = self.client.get(self.url)
        self.assertIn("page_title", response.context)

    def test_context_page_title_is_instance_of_Update_form(self):
        response = self.client.get(self.url)
        self.assertEquals(response.context['page_title'], _("Update User Info"))


class UpdateProfileInfoPostViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory(first_name='abc', last_name='xyz')
        self.client.login(email=self.user.email, password='secret')
        self.url = reverse('update_profile')
        self.data = {
            "first_name": "Test",
            "last_name": "User",
            'email': 'test@test.com',
        }

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "users/profile/update_user_data_form.html")

    def test_context_contains_form_on_error(self):
        response = self.client.post(self.url, data={})
        self.assertIn("form", response.context)

    @override_settings(PROFILE_FORM=UpdateUserDataForm)
    def test_it_redirect_to_success_url(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse('site:profile:index'), fetch_redirect_response=False)

    @override_settings(PROFILE_FORM=UpdateUserDataForm)
    def test_message_value_when_data_posted_successfully(self):
        response = self.client.post(self.url, data=self.data)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(str(msgs[0]), _('your profile has been updated successfully'))


class UpdateEmailViewGetTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(username='test@test.test', password='secret')
        self.client.login(username=self.user.email, password='secret')
        self.url = reverse('email-update')

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url, fetch_redirect_response=False)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "users/profile/update_email_form.html")

    def test_context_contains_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_context_contains_page_title(self):
        response = self.client.get(self.url)
        self.assertIn("page_title", response.context)

    def test_context_page_title_is_instance_of_Update_form(self):
        response = self.client.get(self.url)
        self.assertEquals(response.context['page_title'], _("Update Email"))


class UpdateEmailViewPostTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(username='test@test.test', password='secret')
        self.client.login(username=self.user.email, password='secret')
        self.url = reverse('email-update')
        self.data = {
            "new_email": 'test101@test.test',
            "password": "secret",
        }

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "users/profile/update_email_form.html")

    def test_context_contains_form(self):
        response = self.client.post(self.url)
        self.assertIn("form", response.context)

    def test_it_redirect_to_success_url(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse('site:profile:index'))


class UpdatePhoneViewGETTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(phone="+201005263988")
        self.client.login(email=self.user.email, password='secret')
        self.url = reverse('phone-update')

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "users/profile/update_phone_number_form.html")

    def test_context_contains_form(self):
        response = self.client.get(self.url)
        self.assertIn("form", response.context)

    def test_context_contains_page_title(self):
        response = self.client.get(self.url)
        self.assertIn("page_title", response.context)

    def test_context_page_title_is_instance_of_Update_form(self):
        response = self.client.get(self.url)
        self.assertEquals(response.context['page_title'], _("Update Phone Number"))


class UpdatePhoneViewTestCase(TestCase):
    def test_it_extends_django_class_base_view(self):
        self.assertTrue(issubclass(PhoneUpdateView, View))

    def test_it_extends_django_login_required_mixin(self):
        self.assertTrue(issubclass(PhoneUpdateView, LoginRequiredMixin))

    def test_it_has_get_attribute(self):
        self.assertTrue(hasattr(PhoneUpdateView, 'get'))

    def test_it_has_post_attribute(self):
        self.assertTrue(hasattr(PhoneUpdateView, 'post'))

    def test_get_attribute_is_callable(self):
        self.assertTrue(callable(PhoneUpdateView.get))

    def test_post_attribute_is_callable(self):
        self.assertTrue(callable(PhoneUpdateView.post))

    def test_get_signature(self):
        expected_signature = ['self', 'request', ]
        actual_signature = inspect.getfullargspec(PhoneUpdateView.get)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_post_signature(self):
        expected_signature = ['self', 'request', ]
        actual_signature = inspect.getfullargspec(PhoneUpdateView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class UpdatePhoneViewPOSTTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(phone="+201001452369")
        self.client.login(username=self.user.email, password='secret')
        self.url = reverse('site:profile:phone-update')
        self.data = {
            "new_phone": '+201005263977',
            "password": "secret",
        }

    def test_it_redirects_to_login_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse('login') + '?next=' + self.url)

    def test_template_used(self):
        response = self.client.post(self.url)
        self.assertTemplateUsed(response, "users/profile/update_phone_number_form.html")

    def test_context_contains_form(self):
        response = self.client.post(self.url)
        self.assertIn("form", response.context)

    def test_it_rerender_form_on_failure(self):
        UserFactory(phone='+201005263977')
        response = self.client.post(self.url, self.data)
        self.assertTemplateUsed(response, "users/profile/update_phone_number_form.html")

    def test_it_redirect_to_success_url(self):
        response = self.client.post(self.url, data=self.data)
        self.assertRedirects(response, reverse('site:profile:index'))
