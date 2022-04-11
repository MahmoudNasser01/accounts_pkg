from accounts.verify_phone import VerifyPhoneServiceAbstract


class MockVerifyService(VerifyPhoneServiceAbstract):
    phone = "201002536987"
    code = "777777"

    def send(self, phone):
        return True

    def check(self, phone, code):
        return phone == self.phone and code == self.code


class TestingVerifyService(VerifyPhoneServiceAbstract):
    def send(self, phone):
        return True

    def check(self, phone, code):
        return True
