from typing import Any, Type

import urllib.parse

import requests
from rest_framework import serializers


class ApiClient:
    def __init__(
        self, url: str, serializer_class: Type[serializers.Serializer]
    ) -> None:
        self.serializer_class = serializer_class
        self.url = url

    def get(self, pk: str, **query) -> Any:
        url = f"{self.url}/{pk}/"
        return self._deserialize(self._get(url, **query))

    def list(self, **query):
        for item in self._get(self.url, query):
            yield self._deserialize(item)

    def _deserialize(self, data: Any) -> Any:
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            raise TypeError(
                "; ".join(
                    f"{key}: {err}" for key, err in serializer.error_messages.items()
                )
            )

        return serializer.validated_data

    def _get(self, url: str, query: Any) -> Any:
        res = requests.get(url, query=query)
        if not res.ok:
            raise OSError(f"{url}: http {res.status_code}")

        return res.json()
