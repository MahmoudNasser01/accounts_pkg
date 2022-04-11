## TODO
* Views
  * [x] LoginView
  * [x] RegisterView
  * [x] ResendVerificationOTPView
  * [x] VerifyPhoneView
  * [x] PhoneVerificationCompleteView
  * [x] VerifyEmailView
  * [x] EmailVerificationCompleteView
  * [x] ChangeEmailView
  * [x] ChangePhoneView
  * [x] ChangeProfileView
* APIViews
  * [X] LoginAPIView
  * [x] RegisterAPIView
  * [x] ResendVerificationOTPAPIView
  * [x] VerifyPhoneAPIView
  * [x] ResendVerificationEmailAPIView
  * [x] VerifyEmailAPIView
  * [x] ChangeEmailAPIView
  * [x] ChangePhoneAPIView
  * [x] ChangeProfileAPIView
  * [x] PasswordChangeAPIView
  * [x] LogoutAPIView
  * [ ] PasswordResetAPIView
* Forms and Form Fields
  * [ ] LoginForm
  * [ ] RegisterForm
  * [ ] ResendVerificationOTPForm
  * [ ] VerifyPhoneForm
  * [ ] VerifyEmailForm
  * [ ] ChangeEmailForm
  * [ ] ChangePhoneForm
  * [ ] ChangeProfileForm
  * [ ] PasswordChangeForm
  * [ ] PasswordResetForm
* Services
* Models



## Models


In your `User` model add the following fields

```python
from django.db import models

email_verified_at = models.DateTimeField(blank=True, null=True)
```

### Registration

`RegisterView` will handle the registration process. if you want to implement your registration logic create
new `RegisterForm` and pass it to settings file

```
REGISTER_FORM = NewRegisterForm
```

### Phone Authentication

Add `phone` field and `email_verified_at` field to `User` model

```python
from django.db import models
from django.utils.translation import gettext_lazy as _

phone = models.CharField(max_length=50, blank=False, null=False, unique=True,
                         error_messages={'unique': _("A user with that phone already exists.")})
phone_verified_at = models.DateTimeField(blank=True, null=True)
```

and in `settings` file set

```python
PHONE_AUTHENTICATION_ACTIVE = True

AUTHENTICATION_BACKENDS = (
    # ...
    'apps.users.auth.backends.UsernameOrPhoneModelBackend',
    # ...     
)
```
