from django.test import TestCase

from accounts.factories import UserFactory
from accounts.tokens import account_activation_token


class TestAccountActivationToken(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_it_create_token_for_the_user(self):
        token = account_activation_token.make_token(self.user)
        self.assertGreater(len(token), 0)

    def test_it_valid_token(self):
        token = account_activation_token.make_token(self.user)
        self.assertTrue(account_activation_token.check_token(self.user, token))
