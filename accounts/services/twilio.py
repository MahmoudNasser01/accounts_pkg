from apps.users.auth.verify_phone import VerifyPhoneServiceAbstract
from django.conf import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

Twilio_Client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
Twilio_Client_Verify = Twilio_Client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID)


class VerifyPhoneService(VerifyPhoneServiceAbstract):
    def send(self, phone):
        Twilio_Client_Verify.verifications.create(to=phone, channel='sms')

    def check(self, phone, code):
        try:
            result = Twilio_Client_Verify.verification_checks.create(to=phone, code=code)
        except TwilioRestException:
            return False
        return result.status == 'approved'
