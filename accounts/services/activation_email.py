from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _

from accounts.tokens import account_activation_token


def send_mail_confirmation(request, user):
    current_site = get_current_site(request)
    mail_subject = _('Activate your account.')
    message = render_to_string('accounts/confirm_email_template.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [user.email])
