from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class UsernameOrPhoneModelBackend(ModelBackend):
    def authenticate(self, request, username=None, phone=None, password=None, **kwargs):
        query = None

        if phone:
            query = {"phone": phone}

        elif username:
            query = {UserModel.USERNAME_FIELD: username}

        elif username is None and kwargs.get(UserModel.USERNAME_FIELD):
            query = {UserModel.USERNAME_FIELD: kwargs.get(UserModel.USERNAME_FIELD)}

        if not query or not password:
            return

        try:
            user = UserModel.objects.get(**query)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
