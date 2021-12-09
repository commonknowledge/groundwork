from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    cast,
)

import uuid
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO

import requests
from django.db import models
from rest_framework import parsers, serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from groundwork.core.cron import register_cron

ResourceT = TypeVar("ResourceT")


class Datasource(Generic[ResourceT], metaclass=ABCMeta):
    """
    Abstract interface for reading from an external resource.

    For most REST APIs, unless you are wrapping an existing client library, you probably want to use the subclass
    `ApiClient` instead of this class.
    """

    resource_type: Type[ResourceT]
    """
    Class that API responses should be deserialized into.
    """

    identifer: str = "id"
    """
    An attribute of `ResourceT` that will re-fetch the resource when passed to `get()`.
    
    This will usually be `id` and that is the default.
    """

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @abstractmethod
    def list(self, **kwargs: Dict[str, Any]) -> Iterable[ResourceT]:
        pass

    @abstractmethod
    def get(self, id: Any) -> ResourceT:
        pass

    def get_id(self, resource):
        return getattr(resource, self.identifer)


class MockDatasource(Datasource[ResourceT]):
    """
    Simple in-memory datasource useful for stubbing out remote APIs in tests.
    """

    def __init__(
        self, data: List[ResourceT], identifer: str = "id", **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self.data = data
        self.identifer = identifer

    def list(self, **kwargs: Any) -> Iterable[ResourceT]:
        return self.data

    def get(self, id: str) -> ResourceT:
        return next(x for x in self.data if getattr(x, self.identifer) == id)


class RestDatasource(Datasource[ResourceT]):
    """
    Base class for implementing Rest API clients and converting their responses to resource objects.

    Responses are validated using a django-rest Serializer to ensure that the returned data matches the types declared
    on the resource type.

    You are encouraged to use Python's inbuilt [`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
    decorator and define type hints when defining these classes as this allows type-safe serializers to be
    auto-generated and decreases the amount of boilerplate code that you need to write.

    Provides reasonable default behaviour for get and list operations. You will likely want to subclass this for each
    external service to acommodate differing behaviours around things like pagination.

    Class variables can all either be provided as keyword-args to the constructor, or overridden in subclasses.

    Conforms to the `Datasource` interface, so instances of APIClient can be provided to `SyncedModel`s as their
    datasource.
    """

    serializer_class: Type[serializers.Serializer]
    """
    A django-rest [serializer](https://www.django-rest-framework.org/api-guide/serializers/) used to deserialize API
    responses into instances of the dataclass.

    Can be overridden in subclasses or provided as a kwarg to the initializer.

    If not provided, a serializer is generated from the class provided in `resource_type`. You only need to provide a
    serializer if the resource type is not decorated with the `@dataclass` decorator, or you have custom serialization
    requirements.
    """

    parser_class: Type[parsers.BaseParser] = parsers.JSONParser
    """
    A django-rest [parser](https://www.django-rest-framework.org/api-guide/parsers/) used to parse API responses for processing by the serializer.

    Can be overridden in subclasses or provided as a kwarg to the initializer.

    If not provided, assumes you are dealing with json API responses using the same 'snake_case' conventions as Python
    attribute names.
    """

    base_url: str = ""
    """
    Base API url prepended to `path` to produce the full endpoint url.

    Can be overridden in subclasses or provided as a kwarg to the initializer.
    """

    path: str = ""
    """
    Prepended to `base_url` to produce the full endpoint url.

    Can be overridden in subclasses or provided as a kwarg to the initializer.
    """

    filter: Optional[Callable[[ResourceT], bool]] = None
    """
    Filter returned resources to those matching this predicate.

    Can be overridden in subclasses or provided as a kwarg to the initializer.
    """

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super().__init__(**kwargs)

        self.url = f"{self.base_url}{self.path}"
        self.parser = self.parser_class()

        assert self.resource_type is not None

        if getattr(self, "serializer_class", None) is None:
            self.serializer_class = type(
                f"{self.resource_type.__name__}Serializer",
                (DataclassSerializer,),
                {"Meta": type("Meta", (), {"dataclass": self.resource_type})},
            )

    def get(self, id: str, **kwargs: Dict[str, Any]) -> ResourceT:
        """
        Get a resource by id, deserialize to the resource_type and return.

        The default implementation creates the resource url by appending the id to the endpoint url.

        Args:
            id: External identifier for the fetched resource
            **kwargs: Query params passed to the API call.

        Returns:
            A resource instance representing the remote datasource.
        """

        url = f"{self.url}/{id}/"
        return self.deserialize(self.fetch_url(url, kwargs))

    def list(self, **kwargs: Dict[str, Any]) -> Iterable[ResourceT]:
        """
        List, or search.

        The default implementation creates the resource url by appending the id to the endpoint url.

        Args:
            **kwargs: Query params passed to the API call.

        Yields:
            Resource instances representing the remote datasource.
        """

        for item in self.paginate(**kwargs):
            instance = self.deserialize(item)

            if self.filter is None or self.filter(instance):
                yield instance

    def get_headers(self) -> Dict[str, str]:
        """
        Headers to add to requests. Defaults implementation returns none.

        Returns:
            Dictionary of headers
        """
        return {}

    def deserialize(self, data: Any) -> ResourceT:
        """
        Deserialize raw data representation returned by the API into an instance of resource_type.

        Override this for advanced customization of resource deserialization. You will rarely need to do this as it is
        generally easier to provide a custom `serializer_class`

        The default implementation validates and returns a deserialized instance by calling through to `deserializer_class`.

        Args:
            data: Raw (parsed but still serialized) data representation of the remote resource.

        Raises:
            TypeError: If validating the returned data fails.

        Returns:
            An instance of this resource's resource_type type.

        """

        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            errors = serializer.errors.items()
            raise TypeError("; ".join(f"{key}: {str(err)}" for key, err in errors))

        return cast(ResourceT, serializer.validated_data)

    def fetch_url(self, url: str, query: Dict[str, Any]) -> Any:
        """
        Get a resource by URL and return its raw (parsed but not deserialized) response data.

        Override this to customize how HTTP GET requests are made. The list() method will

        The default implementation validates that the request is successful then parses the response data using `parser_class`.

        Args:
            url: URL of the fetched resource
            query: Query params passed to the GET request.

        Raises:
            OSError: If the server response does not have a 2xx status code.

        Returns:
            Raw (parsed but still serialized) data representation of the remote resource identified by `url`.

        """

        res: requests.Response = requests.get(
            url, params=query, headers=self.get_headers()
        )

        if not res.ok:
            raise OSError(f"{url}: http {res.status_code}")

        return self.parser.parse(
            BytesIO(res.content), media_type=res.headers.get("content-type")
        )

    def paginate(self, **query: Dict[str, Any]) -> Iterable[ResourceT]:
        """
        List this resource and return an iterable of raw representations.

        Override to customize how list() calls are paginated between or the url is constructed.

        If you override this to support pagination, you should yield instances rather than returning a list.

        The default implementation does not perform pagination – it expects the response data to be a simple list of
        resources.

        Args:
            query: Query params passed to the GET request.

        Yields:
            Raw (parsed but still serialized) resource objects.
        """

        yield from self.fetch_url(self.url, query)


@dataclass
class SyncConfig:
    """
    Config object defining how subclasses of `SyncedModel` sync with an external datasource.
    """

    datasource: Datasource[Any]
    """
    External resource to periodically sync this model with
    """

    external_id: str = "external_id"
    """
    Field on both the external resource and this model that is used to map values returned from the external service
    onto instances of the model.
    """

    field_map: Optional[Dict[str, str]] = None
    """
    Map from fields in the model to fields in the external resource.
    """

    sync_interval: Optional[timedelta] = timedelta(days=1)
    """
    Frequency with which the model should be synced from the external source.

    Defaults to one day. If set to `None`, this model will _never_ refresh itself from the external source and only
    populate when referenced by another synced model, or `sync()` is explicitly called.
    """


class SyncedModel(models.Model):
    """
    Base class for models are fetched on a schedule from a remote data source.

    Models that subclass this class must declare a `sync_config` attribute, which configures the remote
    resource to pull from and how to merge it into the database.
    """

    class Meta:
        abstract = True

    last_sync_time = models.DateTimeField()
    """
    Last time this resource was updated from the datasource.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    """
    SyncedModels need to have a uuid primary key to handle recursive references when syncing.
    """

    sync_config: SyncConfig
    """
    Configuration object defining the datasource and how to sync it. Required for all non-abstract subclasses.
    """

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        # Validate the SyncConfig
        if not cls.Meta.abstract and getattr(cls, "sync_config", None) is None:
            raise TypeError("Subclasses of SyncedModel defined `sync_config`")

        # Register the subclass with the cron manager
        if not cls.Meta.abstract and cls.sync_config.sync_interval is not None:
            register_cron(cls.sync, cls.sync_config.sync_interval)

    @classmethod
    def sync(cls):
        """
        Synchronizes the class immediately.
        """
        from groundwork.core.internal.sync_manager import SyncManager

        SyncManager().sync_model(cls)
