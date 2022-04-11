import inspect

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone, dateformat
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..factories import UserFactory
from ..tokens import account_activation_token
from ..views_api import UpdateProfileDataAPIView, UpdateEmailAPIView, UpdatePhoneAPIView, \
    VerifyPhoneAPIView, VerifyEmailAPIView, ResendPhoneConfirmationAPIView, UserLogoutAPIView


# test auth

class SimpleJWTLoginTestCase(TestCase):
    def setUp(self):
        self.url = reverse('api-v1:accounts:token_obtain_pair')
        self.user = UserFactory()
        self.client = APIClient()

    def test_it_return_401_if_not_active_user_tried_to_autheticate(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, {'email': self.user.email, 'password': '123'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_return_401_if_user_does_not_exist(self):
        response = self.client.post(self.url, {'email': 'not_exist', 'password': '123'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_return_401_if_password_is_wrong(self):
        response = self.client.post(self.url, {'email': self.user.email, 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_return_200_if_user_is_valid(self):
        response = self.client.post(self.url, {'email': self.user.email, 'password': 'secret'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_it_return_access_token_after_user_is_authenticated_correctly(self):
        response = self.client.post(self.url, {'email': self.user.email, 'password': 'secret'})
        self.assertTrue('access' in response.data)

    def test_it_return_refresh_token_after_user_is_authenticated_correctly(self):
        response = self.client.post(self.url, {'email': self.user.email, 'password': 'secret'})
        self.assertTrue('refresh' in response.data)

    def test_it_return_401_if_invalid_token_was_given(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'abc')
        response = client.get(reverse('api-v1:accounts:verify-phone'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_the_returned_token_is_valid(self):
        client = APIClient()
        response = client.post(self.url, {'email': self.user.email, 'password': 'secret'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        token = response.data['access']
        client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token))
        response = client.get(reverse('api-v1:accounts:resend-email-activation'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# logout

class TestUserLogoutViewStructure(TestCase):
    def test_it_extends_api_view_class(self):
        self.assertTrue(issubclass(UserLogoutAPIView, APIView))

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(UserLogoutAPIView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(UserLogoutAPIView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UserLogoutAPIView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class TestUserLogoutView(TestCase):
    def setUp(self):
        self.url = reverse('api-v1:accounts:token_obtain_pair')
        self.user = UserFactory()
        self.client = APIClient()
        login_response = self.client.post(self.url, {'email': self.user.email, 'password': 'secret'})
        self.refresh = login_response.data['refresh']
        self.token = login_response.data['access']

    def test_it_return_401_if_user_not_logged_in(self):
        response = self.client.post(reverse('api-v1:accounts:logout'), {'refresh': self.refresh})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_return_204_if_user_is_logged_out(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.token))
        response = self.client.post(reverse('api-v1:accounts:logout'), {'refresh': self.refresh})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_it_return_400_if_invalid_token_was_given(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.token))
        response = self.client.post(reverse('api-v1:accounts:logout'), {'refresh': 'abc'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserSignupAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.url = reverse('api-v1:accounts:signup')
        self.data = {
            "email": "test@test.test",
            "username": "TestUser",
            "phone": "+201005263988",
            "password1": "newTESTPasswordD",
            "password2": "newTESTPasswordD",
            "gender": "male",
            "birthdate": dateformat.format(timezone.now(), 'Y-m-d'),
        }

    def test_it_returns_422_when_data_is_invalid(self):
        """
            set Up :
              - we are trying post empty registration form data to serializer
            result : returning response 422 the data you posted not valid
        """
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code, 422)

    def test_it_returns_201_when_user_created_successfully(self):
        """
              set Up :
                - we are trying post registration data to serializer
              result : returning response 201 the data you posted is right and create product
        """
        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 201)

    def test_it_create_send_the_email(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Activate your account.')

    def test_it_return_access_and_refresh_tokens_once_user_is_signup(self):
        response = self.client.post(self.url, self.data)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)


# phone verification
class VerifyPhoneAPIViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(VerifyPhoneAPIView, APIView))

    def test_view_has_method_post(self):
        self.assertTrue(hasattr(VerifyPhoneAPIView, 'post'))

    def test_view_has_method_post_is_callable(self):
        self.assertTrue(callable(VerifyPhoneAPIView.post))

    def test_post_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(VerifyPhoneAPIView.post)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyPhoneAPIViewPOSTTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(phone="12312123")
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse("api-v1:accounts:verify-phone")
        self.data = {"code": "777777"}

    def test_it_return_401_status_code_if_user_is_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEquals(response.status_code, 401)

    def test_it_return_200_if_user_is_verified(self):
        user = UserFactory(phone_verified_at=now())
        self.client.login(email=user.email, password="secret")
        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 200)

    def test_it_updates_phone_verified_at_column_in_user_model_to_now_on_success(self):
        self.client.post(self.url, self.data)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.phone_verified_at)

    def test_it_raise_422_status_code_for_invalid_data(self):
        self.data = {"code": ""}
        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 422)

    def test_it_return_400_bad_request_user_was_verified_before(self):
        self.user.phone_verified_at = now()
        self.user.save()
        response = self.client.post(self.url, self.data)
        self.assertEquals(response.status_code, 400)


class ResendPhoneConfirmationViewStructureTestCase(TestCase):
    def test_it_extends_django_LoginView(self):
        self.assertTrue(issubclass(ResendPhoneConfirmationAPIView, APIView))

    def test_it_permission_classes_has_is_authenticated(self):
        self.assertIn(IsAuthenticated, ResendPhoneConfirmationAPIView.permission_classes)

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(ResendPhoneConfirmationAPIView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(ResendPhoneConfirmationAPIView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(ResendPhoneConfirmationAPIView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class PhoneConfirmationViewGETTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse("api-v1:accounts:resend_phone_activation")

    def test_it_returns_status_code_of_401_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 401)

    def test_it_return_200_status_code_if_code_was_resent_successfully(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_response_message_value(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data['message'], _('Code was resent successfully.'))


# email verification

class VerifyEmailViewStructureTestCase(TestCase):
    def test_it_extends_django_view_class(self):
        self.assertTrue(issubclass(VerifyEmailAPIView, APIView))

    def test_view_has_method_get(self):
        self.assertTrue(hasattr(VerifyEmailAPIView, 'get'))

    def test_view_has_method_get_is_callable(self):
        self.assertTrue(callable(VerifyEmailAPIView.get))

    def test_get_method_signature(self):
        expected_signature = ['self', 'request', 'uidb64', 'token']
        actual_signature = inspect.getfullargspec(VerifyEmailAPIView.get)[0]
        self.assertEquals(actual_signature, expected_signature)


class VerifyEmailAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)

    def test_it_activate_the_user(self):
        response = self.client.get(reverse('api-v1:accounts:verify-email', args=[self.uid, self.token]))
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.email_verified_at)

    def test_it_return_200_status_code_when_email_was_confirmed_successfully(self):
        response = self.client.get(reverse('api-v1:accounts:verify-email', args=[self.uid, self.token]))
        self.assertEquals(response.status_code, 200)

    def test_message_value_when_email_was_verified(self):
        response = self.client.get(reverse('api-v1:accounts:verify-email', args=[self.uid, self.token]))
        self.assertEquals(response.data['message'], _('Email was verified successfully.'))


class UpdateProfileDataAPIViewStructureTestCase(TestCase):
    def test_it_extends_django_LoginView(self):
        self.assertTrue(issubclass(UpdateProfileDataAPIView, APIView))

    def test_it_permission_classes_has_is_authenticated(self):
        self.assertIn(IsAuthenticated, UpdateProfileDataAPIView.permission_classes)

    def test_view_has_method_put(self):
        self.assertTrue(hasattr(UpdateProfileDataAPIView, 'put'))

    def test_view_has_method_put_is_callable(self):
        self.assertTrue(callable(UpdateProfileDataAPIView.put))

    def test_put_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UpdateProfileDataAPIView.put)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_get_serializer_class_method(self):
        self.assertIn('get_serializer_class', UpdateProfileDataAPIView.__dict__)


class UpdateProfileDataAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse('api-v1:accounts:profile_info')
        self.data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            "gender": "male",
            "birthdate": "2000-2-2",
        }

    def tearDown(self):
        self.client.logout()

    def test_it_through_exception_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.put(self.url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_returns_status_code_of_201_if_data_profile_is_updated(self):
        response = self.client.put(self.url, self.data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_it_return_422_for_invalid_data(self):
        self.data['birthdate'] = 'invalid'
        response = self.client.put(self.url, self.data)
        self.assertEquals(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_it_returns_user_data_after_updated(self):
        response = self.client.put(self.url, self.data)
        self.assertIsNotNone(response.data)

    def test_it_returns_201_when_user_created_successfully(self):
        response = self.client.put(self.url, data=self.data)
        self.assertEquals(response.status_code, 201)


class UpdateEmailAPIViewStructureTestCase(TestCase):
    def test_it_extends_django_LoginView(self):
        self.assertTrue(issubclass(UpdateEmailAPIView, APIView))

    def test_it_permission_classes_has_is_authenticated(self):
        self.assertIn(IsAuthenticated, UpdateEmailAPIView.permission_classes)

    def test_view_has_method_put(self):
        self.assertTrue(hasattr(UpdateEmailAPIView, 'put'))

    def test_view_has_method_put_is_callable(self):
        self.assertTrue(callable(UpdateEmailAPIView.put))

    def test_put_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UpdateEmailAPIView.put)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_get_serializer_class_method(self):
        self.assertIn('get_serializer_class', UpdateEmailAPIView.__dict__)


class UpdateEmailAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(email='test@test.com')
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse('api-v1:accounts:update_email')
        self.data = {
            'new_email': "newtest@test.com",
            "password": "secret",
        }

    def tearDown(self):
        self.client.logout()

    def test_it_through_exception_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.put(self.url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_returns_422_when_data_is_invalid(self):
        response = self.client.put(self.url, data={})
        self.assertEquals(response.status_code, 422)

    def test_it_returns_201_when_user_created_successfully(self):
        response = self.client.put(self.url, data=self.data)
        self.assertEquals(response.status_code, 201)

    def test_it_returns_422_if_user_tried_to_enter_the_same_email(self):
        data = {
            'email': "test@test.com",
            "password": "secret",
        }
        response = self.client.put(self.url, data=data)
        self.assertEquals(response.status_code, 422)

    def test_it_change_email_for_user(self):
        print(self.user.email)
        self.client.put(self.url, data=self.data)
        self.user.refresh_from_db()
        print(self.user.email)
        self.assertEquals(self.user.email, self.data['new_email'])


class UpdatePhoneAPIViewStructure(TestCase):
    def test_it_extends_django_LoginView(self):
        self.assertTrue(issubclass(UpdatePhoneAPIView, APIView))

    def test_it_permission_classes_has_is_authenticated(self):
        self.assertIn(IsAuthenticated, UpdatePhoneAPIView.permission_classes)

    def test_view_has_method_put(self):
        self.assertTrue(hasattr(UpdatePhoneAPIView, 'put'))

    def test_view_has_method_put_is_callable(self):
        self.assertTrue(callable(UpdatePhoneAPIView.put))

    def test_put_method_signature(self):
        expected_signature = ['self', 'request']
        actual_signature = inspect.getfullargspec(UpdatePhoneAPIView.put)[0]
        self.assertEquals(actual_signature, expected_signature)

    def test_it_has_get_serializer_class_method(self):
        self.assertIn('get_serializer_class', UpdatePhoneAPIView.__dict__)


class UpdatePhoneAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(phone='+201005263977')
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(self.refresh.access_token))
        self.url = reverse('api-v1:accounts:update_phone')
        self.data = {
            'new_phone': "+201005263988",
            "password": "secret",
        }

    def tearDown(self):
        self.client.logout()

    def test_it_through_exception_if_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.put(self.url)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_it_returns_422_when_data_is_invalid(self):
        response = self.client.put(self.url, data={})
        self.assertEquals(response.status_code, 422)

    def test_it_returns_201_when_user_created_successfully(self):
        response = self.client.put(self.url, data=self.data)
        self.assertEquals(response.status_code, 201)

    def test_it_returns_201_when_user_old_phone_number_is_equal_to_new_number(self):
        data = {
            'new_phone': "+201005263977",
            "password": "secret",
        }
        response = self.client.put(self.url, data=data)
        self.assertEquals(response.status_code, 422)
