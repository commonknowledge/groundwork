from typing import Any, Callable, Dict, Generic, Iterable, Optional, Type, TypeVar, cast

import urllib.parse
from io import BytesIO

import requests
from rest_framework import parsers, serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from pyck.core.datasource import ExternalResource

DataclassT = TypeVar("DataclassT")


class RestResource(ExternalResource[DataclassT]):
    """
    Base class for implementing Rest API clients and converting their responses to type-safe
    [Dataclass](https://docs.python.org/3/library/dataclasses.html) instances.

    Can be overridden in subclasses or provided as a kwarg to the initializer.

    Provides reasonable default behaviour for get and list operations. You will likely want to subclass this for each
    external service to acommodate differing behaviours around things like pagination.

    Conforms to the `ExternalResource` interface, so instances of APIClient can be provided to `SyncedModel`s as their
    datasource.
    """

    """
    Class that API responses should be deserialized into.

    Can be overridden in subclasses or provided as a kwarg to the initializer.

    You are encouraged to use python's inbuilt @dataclass decorator and define type hints when defining these classes
    as this allows type-safe serializers to be auto-generated and decreases the amount of boilerplate code that you
    need to write.
    """
    dataclass: Type[DataclassT]

    """
    A django-rest [serializer](https://www.django-rest-framework.org/api-guide/serializers/) used to deserialize API
    responses into instances of the dataclass.

    Can be overridden in subclasses or provided as a kwarg to the initializer.

    If not provided, a serializer is generated from the class provided in `dataclass`. You only need to provide a
    serializer if the dataclass type is not decorated with the `@dataclass` decorator, or you have custom serialization
    requirements.
    """
    serializer_class: Type[serializers.Serializer]

    """
    A django-rest [parser](https://www.django-rest-framework.org/api-guide/parsers/) used to parse API responses for processing by the serializer.

    Can be overridden in subclasses or provided as a kwarg to the initializer.

    If not provided, assumes you are dealing with json API responses using the same 'snake_case' conventions as Python
    attribute names.
    """
    parser_class: Type[parsers.BaseParser] = parsers.JSONParser

    """
    Base API url prepended to `path` to produce the full endpoint url.

    Can be overridden in subclasses or provided as a kwarg to the initializer.
    """
    base_url = ""

    """
    Prepended to `base_url` to produce the full endpoint url.

    Can be overridden in subclasses or provided as a kwarg to the initializer.
    """
    path = ""

    """
    Filter returned resources to those matching this predicate.

    Can be overridden in subclasses or provided as a kwarg to the initializer.
    """
    filter: Optional[Callable[[DataclassT], bool]] = None

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super().__init__(**kwargs)

        self.url = f"{self.base_url}{self.path}"
        self.parser = self.parser_class()

        assert self.dataclass is not None

        if getattr(self, "serializer_class", None) is None:
            self.serializer_class = type(
                f"{self.dataclass.__name__}Serializer",
                (DataclassSerializer,),
                {"Meta": type("Meta", (), {"dataclass": self.dataclass})},
            )

    def get(self, id: str, **kwargs: Dict[str, Any]) -> DataclassT:
        """
        Get a resource by id, deserialize to the dataclass and return.

        The default implementation creates the resource url by appending the id to the endpoint url.

        Args:
            id: External identifier for the fetched resource
            **kwargs: Query params passed to the API call.
        """

        url = f"{self.url}/{id}/"
        return self._deserialize(self._get(url, kwargs))

    def list(self, **kwargs: Dict[str, Any]) -> Iterable[DataclassT]:
        """
        List, or search.

        The default implementation creates the resource url by appending the id to the endpoint url.

        Args:
            **kwargs: Query params passed to the API call.
        """

        for item in self._list(**kwargs):
            instance = self._deserialize(item)

            if self.filter is None or self.filter(instance):
                yield instance

    def _deserialize(self, data: Any) -> DataclassT:
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            raise TypeError(
                "; ".join(
                    f"{key}: {err}" for key, err in serializer.error_messages.items()
                )
            )

        return cast(DataclassT, serializer.validated_data)

    def _get(self, url: str, query: Dict[str, Any]) -> Any:
        """
        Get a resource by URL and return its raw (parsed but not deserialized) response data.

        Override to customize how HTTP GET requests are made.

        The default implementation raises an IOError if the response does not have a 2xx status code then parses the
        response data using `parser_class`.

        Args:
            url: URL of the fetched resource
            query: Query params passed to the GET request.
        """

        res: requests.Response = requests.get(url, params=query)
        if not res.ok:
            raise OSError(f"{url}: http {res.status_code}")

        return self.parser.parse(
            BytesIO(res.content), media_type=res.headers.get("content-type")
        )

    def _list(self, **query: Dict[str, Any]) -> Iterable[DataclassT]:
        """
        List this resource and return an iterable of raw (parsed but not deserialized) response data.

        Override to customize how list() calls are paginated between or the url is constructed.

        The default implementation does not perform pagination – it expects the response data to be a simple list of
        resources.

        Args:
            query: Query params passed to the GET request.
        """

        yield from self._get(self.url, query)
