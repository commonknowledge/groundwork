from typing import ABCMeta, Type

from rest_framework import serializers


class ExternalResource(metaclass=ABCMeta):
    serializer_class: Type[serializers.Serializer]

    def list(self):
        pass
