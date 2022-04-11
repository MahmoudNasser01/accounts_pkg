from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.translation import gettext as _
from rest_framework import serializers

from accounts.serializers import LogoutSerializer, RegisterSerializer, UpdateUserDataSerializer, UpdateEmailSerializer, \
    UpdatePhoneNumberSerializer


class RegistrationSerializerTestCase(TestCase):
    def setUp(self):
        self.serializer = RegisterSerializer()

    def test_it_extends_drf_serializer(self):
        self.assertTrue(issubclass(RegisterSerializer, serializers.ModelSerializer))

    def test_it_has_email_field(self):
        self.assertIn('email', self.serializer.fields)

    def test_email_field_is_instance_of_email_field(self):
        self.assertIsInstance(self.serializer.fields['email'], serializers.CharField)

    def test_email_field_is_required(self):
        self.assertTrue(self.serializer.fields['email'].required)

    def test_email_field_max_length_is_100(self):
        self.assertEquals(self.serializer.fields['email'].max_length, 100)

    def test_email_field_help_text(self):
        self.assertEquals(self.serializer.fields['email'].help_text, _("Required, please provide your email"))

    def test_it_has_password1_field(self):
        self.assertIn('password1', self.serializer.fields)

    def test_password1_field_is_instance_of_password1_field(self):
        self.assertIsInstance(self.serializer.fields['password1'], serializers.CharField)

    def test_password1_field_is_required(self):
        self.assertTrue(self.serializer.fields['password1'].required)

    def test_password1_field_help_text(self):
        self.assertEquals(self.serializer.fields['password1'].help_text,
                          password_validation.password_validators_help_text_html())

    def test_it_has_password2_field(self):
        self.assertIn('password2', self.serializer.fields)

    def test_password2_field_is_instance_of_password2_field(self):
        self.assertIsInstance(self.serializer.fields['password2'], serializers.CharField)

    def test_password2_field_is_required(self):
        self.assertTrue(self.serializer.fields['password2'].required)

    def test_password2_field_help_text(self):
        self.assertEquals(self.serializer.fields['password2'].help_text,
                          _("Enter the same password as before, for verification."))

    def test_it_has_username_field(self):
        self.assertIn('username', self.serializer.fields)

    def test_username_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.serializer.fields['username'], serializers.CharField)

    def test_username_field_is_required(self):
        self.assertTrue(self.serializer.fields['username'].required)

    def test_username_field_max_length_is_100(self):
        self.assertEquals(self.serializer.fields['username'].max_length, 100)

    def test_username_field_help_text(self):
        self.assertEquals(self.serializer.fields['username'].help_text, _("Required, please provide your username"))

    def test_it_has_phone_field(self):
        self.assertIn('phone', self.serializer.fields)

    def test_phone_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.serializer.fields['phone'], serializers.CharField)

    def test_phone_field_is_required(self):
        self.assertTrue(self.serializer.fields['phone'].required)

    def test_phone_field_max_length_is_100(self):
        self.assertEquals(self.serializer.fields['phone'].max_length, 100)

    def test_phone_field_help_text(self):
        self.assertEquals(self.serializer.fields['phone'].help_text, _("Required, please provide your phone number"))




class LogoutSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = LogoutSerializer(data={'refresh': 'test'})

    def test_it_has_refresh_field(self):
        self.assertIn('refresh', self.serializer.fields)

    def test_refresh_field_help_text(self):
        self.assertEquals(self.serializer.fields['refresh'].help_text, _("Required, please provide your refresh token"))

    def test_refresh_field_is_instance_of_char_field(self):
        self.assertIsInstance(self.serializer.fields['refresh'], serializers.CharField)

    def test_refresh_field_is_required(self):
        self.assertTrue(self.serializer.fields['refresh'].required)

    def test_it_has_save_method(self):
        self.assertTrue(hasattr(self.serializer, 'save'))




# profile serializer tests

class UpdateUserDataSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = UpdateUserDataSerializer(data={})

    def test_it_has_meta_class(self):
        self.assertIsInstance(self.serializer.Meta, type)

    def test_it_has_model_class_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'model'))

    def test_it_has_fields_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'fields'))

    def test_it_has_first_name_field(self):
        self.assertIn('first_name', self.serializer.fields)

    def test_it_has_last_name_field(self):
        self.assertIn('last_name', self.serializer.fields)

class UpdateEmailSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = UpdateEmailSerializer(data={})

    def test_it_has_meta_class(self):
        self.assertIsInstance(self.serializer.Meta, type)

    def test_it_has_model_class_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'model'))

    def test_it_has_fields_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'fields'))

    def test_it_has_email_field(self):
        self.assertIn('email', self.serializer.fields)

    def test_it_has_password_field(self):
        self.assertIn('password', self.serializer.fields)


class UpdatePhoneSerializerStructureTestCase(TestCase):
    def setUp(self):
        self.serializer = UpdatePhoneNumberSerializer(data={})

    def test_it_has_meta_class(self):
        self.assertIsInstance(self.serializer.Meta, type)

    def test_it_has_model_class_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'model'))

    def test_it_has_fields_in_meta(self):
        self.assertTrue(hasattr(self.serializer.Meta, 'fields'))

    def test_it_has_phone_field(self):
        self.assertIn('phone', self.serializer.fields)

    def test_it_has_password_field(self):
        self.assertIn('password', self.serializer.fields)
