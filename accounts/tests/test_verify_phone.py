from django.test import TestCase, override_settings

from accounts.verify_phone import VerifyPhone, VerifyPhoneServiceAbstract


class VerifyPhoneSendTestCase(TestCase):
    def setUp(self):
        self.phone = "201002536987"

    @override_settings(PHONE_VERIFY_SERVICE="accounts.tests.mocks.MockVerifyService")
    def test_it_calls_the_select_service_send(self):
        success = VerifyPhone().send(phone=self.phone)
        self.assertTrue(success)


class VerifyPhoneCheckTestCase(TestCase):
    def setUp(self):
        self.phone = "201002536987"
        self.code = "777777"

    @override_settings(PHONE_VERIFY_SERVICE="accounts.tests.mocks.MockVerifyService")
    def test_it_calls_the_selected_service_check(self):
        success = VerifyPhone().check(phone=self.phone, code=self.code)
        self.assertTrue(success)

    @override_settings(PHONE_VERIFY_SERVICE="accounts.tests.mocks.MockVerifyService")
    def test_it_returns_false_if_phone_or_code_is_not_correct(self):
        success = VerifyPhone().check(phone="201063598876", code=self.code)
        self.assertFalse(success)


class VerifyPhoneGetServiceClassTestCase(TestCase):
    @override_settings(PHONE_VERIFY_SERVICE="accounts.tests.mocks.MockVerifyService")
    def test_it_returns_subclass_of_verify_phone_abstract(self):
        class_ = VerifyPhone().get_service_class()
        self.assertIsInstance(class_, VerifyPhoneServiceAbstract)
