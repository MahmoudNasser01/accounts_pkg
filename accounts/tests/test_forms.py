from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.test import override_settings
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from accounts.factories import UserFactory
from accounts.forms import PhoneLoginForm, RegisterForm, VerifyPhoneForm
from accounts.forms import UpdateUserDataForm, UpdateEmailForm, UpdatePhoneNumberForm

UserModel = get_user_model()


def get_default_user_data():
    return {
        "email": "test@test.test",
        "username": "Test User",
        "phone": "+201005263988",
        "password1": "newTESTPasswordD",
        "password2": "newTESTPasswordD",
        "first_name": "Test",
        "last_name": "User",
        "gender": "male",
        "birthdate": now(),
    }


def check_required(cls, key):
    data = {**cls.DEFAULT_DATA}
    data.pop(key, None)
    instance = cls.Form(data=data)
    cls.assertFalse(instance.is_valid())
    cls.assertEquals(instance.errors.as_data()[key][0].code, 'required')


def check_unique(cls, key, value):
    data = {**cls.DEFAULT_DATA}
    data.update({key: value})
    instance = cls.Form(data=data)
    cls.assertFalse(instance.is_valid())
    cls.assertEquals(instance.errors.as_data()[key][0].code, 'unique')


class RegistrationFormStructureTestCase(TestCase):
    def setUp(self):
        self.form = RegisterForm()

    def test_it_extends_django_Form(self):
        self.assertTrue(issubclass(RegisterForm, UserCreationForm))

    def test_it_has_email_field(self):
        self.assertIn('email', self.form.fields)

    def test_email_field_is_instance_of_email_field(self):
        self.assertIsInstance(self.form.fields['email'], forms.CharField)

    def test_email_field_max_length_is_100(self):
        self.assertEquals(self.form.fields['email'].max_length, 100)

    def test_email_field_help_text(self):
        self.assertEquals(self.form.fields['username'].help_text, _("Required, please provide your username"))

    def test_it_has_username_field(self):
        self.assertIn('username', self.form.fields)

    def test_username_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['username'], forms.CharField)

    def test_user_name_field_is_required(self):
        self.assertTrue(self.form.fields['username'].required)

    def test_username_field_max_length_is_100(self):
        self.assertEquals(self.form.fields['username'].max_length, 100)

    def test_username_field_help_text(self):
        self.assertEquals(self.form.fields['username'].help_text, _("Required, please provide your username"))

    def test_it_has_phone_field(self):
        self.assertIn('phone', self.form.fields)

    def test_phone_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['phone'], forms.CharField)

    def test_phone_field_is_required(self):
        self.assertTrue(self.form.fields['phone'].required)

    def test_phone_field_max_length_is_100(self):
        self.assertEquals(self.form.fields['phone'].max_length, 100)

    def test_phone_field_help_text(self):
        self.assertEquals(self.form.fields['phone'].help_text, _("Required, please provide your phone number"))


class RegisterFormValidationTest(TestCase):
    def setUp(self):
        self.DEFAULT_DATA = get_default_user_data()
        self.Form = RegisterForm
        UserModel.objects.create_user(
            email='first@aol.com', username="First User", first_name="First",
            last_name="User", phone="+201005263987")

    def test_username_is_required(self):
        check_required(self, 'username')

    def test_phone_is_required(self):
        check_required(self, 'phone')

    def test_phone_is_unique(self):
        check_unique(self, "phone", "+201005263987")

    def test_email_is_required(self):
        check_required(self, 'email')

    def test_email_is_unique(self):
        check_unique(self, "email", "first@aol.com")

    def test_password1_is_required(self):
        check_required(self, 'password1')

    def test_password2_is_required(self):
        check_required(self, 'password2')

    def test_password2_mismatch(self):
        data = self.DEFAULT_DATA
        data.update({
            "password1": "123654789",
            "password2": "123456789"
        })
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()["password2"][0].code, 'password_mismatch')


class PhoneLoginFormStructureTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory()
        self.form = PhoneLoginForm(request=self.request)

    def test_it_extends_django_Form(self):
        self.assertTrue(issubclass(PhoneLoginForm, forms.Form))

    def test_it_has_cached_user(self):
        self.assertTrue(hasattr(self.form, 'user_cache'))

    def test_it_has_get_user_method(self):
        self.assertTrue(hasattr(self.form, 'get_user') and callable(self.form.get_user))

    def test_get_user_method_returns_cache_user_value(self):
        self.assertEquals(self.form.user_cache, self.form.get_user())

    def test_it_has_username_field(self):
        self.assertIn('username', self.form.fields)

    def test_username_field_is_instance_of_email_field(self):
        self.assertIsInstance(self.form.fields['username'], forms.EmailField)

    def test_it_has_phone_field(self):
        self.assertIn('phone', self.form.fields)

    def test_phone_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['phone'], forms.CharField)

    def test_it_has_password_field(self):
        self.assertIn('password', self.form.fields)

    def test_password_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['password'], forms.CharField)

    def test_password_has_label_Password(self):
        self.assertEquals(self.form.fields['password'].label, _('Password'))

    def test_password_field_not_striping_its_value(self):
        form = PhoneLoginForm()
        self.assertFalse(self.form.fields['password'].strip)

    def test_password_widget_is_instance_of_passwordInput(self):
        self.assertIsInstance(self.form.fields['password'].widget, forms.PasswordInput)

    def test_it_has_remember_me_field(self):
        self.assertIn('remember_me', self.form.fields)

    def test_remember_me_field_is_instance_of_charfield(self):
        self.assertIsInstance(self.form.fields['remember_me'], forms.BooleanField)

    def test_remember_me_field_has_label_Remember_Me(self):
        self.assertEquals(self.form.fields['remember_me'].label, _('Remember Me'))

    def test_remember_me_initial_value_is_false(self):
        self.assertEquals(self.form.fields['remember_me'].initial, False)


class PhoneLoginFormValidationTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()
        self.user = UserFactory()
        self.Form = PhoneLoginForm
        self.DEFAULT_DATA = {
            "username": self.user.email,
            "phone": self.user.phone,
            "password": "secret",
            "remember_me": True
        }

    def test_it_fails_if_both_phone_and_user_name_are_not_exist(self):
        self.DEFAULT_DATA.pop('phone')
        self.DEFAULT_DATA.pop('username')
        form = self.Form(request=self.request, data=self.DEFAULT_DATA)
        self.assertFalse(form.is_valid())
        self.assertEquals('phone_or_username_are_required', form.errors.as_data()['__all__'][0].code)
        self.assertEquals(_("Please enter a correct phone or username"), form.errors.as_data()['__all__'][0].message)

    def test_password_is_required(self):
        check_required(self, 'password')

    def test_it_fails_if_password_is_not_correct(self):
        self.DEFAULT_DATA.update({"password": "12345"})
        form = self.Form(request=self.request, data=self.DEFAULT_DATA)
        self.assertFalse(form.is_valid())
        self.assertEquals('invalid_login', form.errors.as_data()['__all__'][0].code)
        self.assertEquals(_(
            "Please enter a correct phone and password. Note that both "
            "fields may be case-sensitive."
        ), form.errors.as_data()['__all__'][0].message)

    def test_it_fails_if_username_is_not_correct(self):
        self.DEFAULT_DATA.pop('phone')
        self.DEFAULT_DATA.update({"username": "aaa@lll.ccc"})
        form = self.Form(request=self.request, data=self.DEFAULT_DATA)
        self.assertFalse(form.is_valid())
        self.assertEquals('invalid_login', form.errors.as_data()['__all__'][0].code)
        self.assertEquals(_(
            "Please enter a correct phone and password. Note that both "
            "fields may be case-sensitive."
        ), form.errors.as_data()['__all__'][0].message)

    def test_it_fails_if_phone_is_not_correct(self):
        self.DEFAULT_DATA.pop('username')
        self.DEFAULT_DATA.update({"phone": "56415615"})
        form = self.Form(request=self.request, data=self.DEFAULT_DATA)
        self.assertFalse(form.is_valid())
        self.assertEquals('invalid_login', form.errors.as_data()['__all__'][0].code)
        self.assertEquals(_(
            "Please enter a correct phone and password. Note that both "
            "fields may be case-sensitive."
        ), form.errors.as_data()['__all__'][0].message)

    def test_it_authenticates_correct_user_by_phone(self):
        self.DEFAULT_DATA.pop('username')
        form = self.Form(request=self.request, data=self.DEFAULT_DATA)
        self.assertTrue(form.is_valid())

    def test_it_authenticates_correct_user_by_username(self):
        self.DEFAULT_DATA.pop('username')
        form = self.Form(request=self.request, data=self.DEFAULT_DATA)
        self.assertTrue(form.is_valid())

    def test_it_saves_authenticated_user_in_user_cache(self):
        self.DEFAULT_DATA.pop('username')
        form = self.Form(request=self.request, data=self.DEFAULT_DATA)
        form.is_valid()
        self.assertEquals(form.user_cache, self.user)

    def test_get_user_method_returns_authenticated_user(self):
        self.DEFAULT_DATA.pop('username')
        form = self.Form(request=self.request, data=self.DEFAULT_DATA)
        form.is_valid()
        print(form.errors)
        self.assertEquals(form.get_user(), self.user)

    def test_it_sets_session_expiry_to_zero_if_remember_me_is_false(self):
        self.DEFAULT_DATA.update({"remember_me": False})
        form = self.Form(request=self.request, data=self.DEFAULT_DATA)
        self.assertTrue(form.is_valid())
        self.assertIn('_session_expiry', self.request.session)
        self.assertEquals(0, self.request.session['_session_expiry'])


class VerifyPhoneFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(phone="201002536987")
        self.form = VerifyPhoneForm(user=self.user)

    def test_it_extends_django_Form(self):
        self.assertIsInstance(self.form, forms.Form)

    def test_it_has_code_field(self):
        self.assertIn('code', self.form.fields)

    def test_code_label_is_correct(self):
        self.assertEquals(self.form.fields['code'].label, _("message sent to phone number: {}".format(self.user.phone)))

    def test_code_min_length_is_six_characters(self):
        self.assertEquals(self.form.fields['code'].min_length, 6)

    def test_code_max_length_is_six_characters(self):
        self.assertEquals(self.form.fields['code'].max_length, 6)


class VerifyPhoneFormValidationTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(phone="201002536987")
        self.data = {"code": "777777"}

    @override_settings(PHONE_VERIFY_SERVICE="apps.users.auth.tests.mocks.MockVerifyService")
    def test_it_fails_if_phone_verification_is_not_successful(self):
        self.data.update({"code": "888888"})
        form = VerifyPhoneForm(user=self.user, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertEquals('invalid_code', form.errors.as_data()['__all__'][0].code)
        self.assertEquals(_("The Provided code is Properly invalid"), form.errors.as_data()['__all__'][0].message)

    @override_settings(PHONE_VERIFY_SERVICE="apps.users.auth.tests.mocks.MockVerifyService")
    def test_it_passes_if_phone_verification_is_successful(self):
        form = VerifyPhoneForm(user=self.user, data=self.data)
        self.assertTrue(form.is_valid())


# profile tests

class UpdateUserDataFormStructureTestCase(TestCase):
    def setUp(self):
        self.form = UpdateUserDataForm()
        self.DEFAULT_DATA = get_default_user_data()

    def test_form_class_is_subclass_from_model_form(self):
        self.assertTrue(issubclass(UpdateUserDataForm, forms.ModelForm))

    def test_form_has_meta_class(self):
        self.assertTrue(hasattr(self.form, 'Meta'))

    def test_form_model_is_user_model(self):
        self.assertEquals(self.form.Meta.model, UserModel)

    def test_form_fields_are_equal_to_user_model_fields(self):
        self.assertEquals(self.form.Meta.fields, ('first_name', 'last_name', 'gender', 'birthdate', 'image'))

    def test_it_has_clean_first_name(self):
        self.assertTrue(hasattr(self.form, 'clean_first_name'))

    def test_it_has_clean_last_name(self):
        self.assertTrue(hasattr(self.form, 'clean_last_name'))

    def test_html_representation_has_first_name_field(self):
        self.assertIn('name="first_name"', str(self.form))

    def test_html_representation_has_last_name_field(self):
        self.assertIn('name="last_name"', str(self.form))

    def test_html_representation_has_gender_field(self):
        self.assertIn('name="gender"', str(self.form))

    def test_html_representation_birthdate_field(self):
        self.assertIn('name="birthdate"', str(self.form))

    def test_html_representation_image_field(self):
        self.assertIn('name="image"', str(self.form))


class UpdateUserFormValidationTest(TestCase):
    def setUp(self):
        self.DEFAULT_DATA = get_default_user_data()
        self.Form = UpdateUserDataForm

    def test_update_user_data_form(self):
        form = UpdateUserDataForm(data=self.DEFAULT_DATA)
        self.assertTrue(form.is_valid())

    def test_update_user_data_form_with_empty_first_name(self):
        check_required(self, 'first_name')

    def test_update_user_data_form_with_empty_last_name(self):
        check_required(self, 'last_name')

    def test_it_rais_error_message_if_no_first_name(self):
        self.DEFAULT_DATA.pop('first_name')
        form = UpdateUserDataForm(data=self.DEFAULT_DATA)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['first_name'][0].code, 'required')

    def test_it_rais_error_message_if_no_last_name(self):
        self.DEFAULT_DATA.pop('last_name')
        form = UpdateUserDataForm(data=self.DEFAULT_DATA)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['last_name'][0].code, 'required')


class UpdateEmailFormStructureTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        self.user = UserFactory(email='test@test.test', password='secret')
        self.Form = UpdateEmailForm
        self.DEFAULT_DATA = {
            "new_email": 'new_test@test.test',
            "password": "secret",
        }

    def test_form_class_is_subclass_from_forms_form(self):
        self.assertTrue(issubclass(UpdateEmailForm, forms.Form))

    def test_html_representation_has_new_email_field(self):
        self.assertIn('name="new_email"', str(self.Form()))

    def test_html_representation_has_password_field(self):
        self.assertIn('name="password"', str(self.Form()))

    def test_form_has_error_messages_field(self):
        self.assertTrue(hasattr(self.Form, 'error_messages'))

    def test_it_has_clean_new_email(self):
        self.assertTrue(hasattr(self.Form, 'clean_new_email'))

    def test_it_has_clean_password(self):
        self.assertTrue(hasattr(self.Form, 'clean_password'))

    def test_it_has_save(self):
        self.assertTrue(hasattr(self.Form, 'save'))


class UpdateEmailFormValidationTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        self.user = UserFactory(email='test@test.test', password='secret')
        self.Form = UpdateEmailForm
        self.DEFAULT_DATA = {
            "new_email": 'new_test@test.test',
            "password": "secret",
        }

    def test_email_form(self):
        form = UpdateEmailForm(data=self.DEFAULT_DATA, user=self.user)
        self.assertTrue(form.is_valid())

    def test_email_from_throw_error_if_provides_incomplete_data(self):
        form = UpdateEmailForm(data={}, user=self.user)
        self.assertFalse(form.is_valid())

    def test_email_from_throw_error_if_email_is_email_is_already_exists(self):
        default_data = {
            "new_email": 'test@test.test',
            "password": "secret",
        }
        form = UpdateEmailForm(data=default_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['new_email'][0].code, 'unique')

    def test_email_field_throw_error_if_old_email_equal_new_email(self):
        default_data = {
            "new_email": 'test@test.test',
            "password": "secret",
        }
        form = UpdateEmailForm(data=default_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.errors.as_data()['new_email'][0].code, 'unique')

    def test_email_from_throw_error_if_email_is_invalid(self):
        data = {
            "new_email": 'fake',
            "password": "secret",
        }
        form = UpdateEmailForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['new_email'][0].code, 'invalid')

    def test_email_from_throw_error_if_password_is_invalid(self):
        data = {
            "new_email": 'test@test.sdfsd',
            'password': 'fake',
        }

        form = UpdateEmailForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['password'][0].code, 'invalid')

    def test_ti_change_user_email(self):
        data = {
            "new_email": 'new@new.com',
            "password": "secret",
        }
        form = UpdateEmailForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.user.email, 'new@new.com')


class UpdatePhoneFormTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory()
        self.form = UpdatePhoneNumberForm()

    def test_it_extends_django_Form(self):
        self.assertIsInstance(UpdatePhoneNumberForm(), forms.Form)

    def test_it_has_phone_field(self):
        self.assertIn('new_phone', self.form.fields)

    def test_phone_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['new_phone'], forms.CharField)

    def test_phone_field_is_required(self):
        self.assertTrue(self.form.fields['new_phone'].required)

    def test_it_has_password_field(self):
        self.assertIn('password', self.form.fields)

    def test_password_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.form.fields['password'], forms.CharField)

    def test_password_has_label_Password(self):
        self.assertEquals(self.form.fields['password'].label, _("Your Password"))

    def test_password_field_not_striping_its_value(self):
        form = UpdateEmailForm()
        self.assertFalse(self.form.fields['password'].strip)

    def test_password_widget_is_instance_of_passwordInput(self):
        self.assertIsInstance(self.form.fields['password'].widget, forms.PasswordInput)


class UpdatePhoneFormValidationTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        self.user = UserFactory(phone="+201005263988")
        self.DEFAULT_DATA = get_default_user_data()
        self.Form = UpdatePhoneNumberForm
        self.DEFAULT_DATA = {
            "new_phone": '+201005263977',
            "password": "secret",
        }

    def test_phone_form(self):
        form = UpdatePhoneNumberForm(data=self.DEFAULT_DATA, user=self.user)
        self.assertTrue(form.is_valid())

    def test_phone_from_throw_error_if_provides_incomplete_data(self):
        form = UpdatePhoneNumberForm(data={}, user=self.user)
        self.assertFalse(form.is_valid())

    def test_phone_from_throw_error_if_new_phone_already_exists(self):
        default_data = {
            "new_phone": '+201005263988',
            "password": "secret",
        }
        form = UpdatePhoneNumberForm(data=default_data, user=self.user)
        self.assertFalse(form.is_valid())
