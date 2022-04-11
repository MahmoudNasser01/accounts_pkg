import importlib
from abc import ABC, abstractmethod

from django.conf import settings


class VerifyPhoneServiceAbstract(ABC):
    class Meta:
        abstract = True

    @abstractmethod
    def send(self, phone):
        pass

    @abstractmethod
    def check(self, phone, code):
        pass


class VerifyPhone:
    def __init__(self):
        self.service = self.get_service_class()

    def send(self, phone):
        return self.service.send(phone)

    def check(self, phone, code):
        return self.service.check(phone, code)

    @staticmethod
    def get_service_class():
        service_name = settings.PHONE_VERIFY_SERVICE
        split_service_name = service_name.split('.')
        class_name = split_service_name[-1:][0]
        module_name = split_service_name[:-1]
        service_class = getattr(importlib.import_module('.'.join(module_name)), class_name)
        return service_class()
