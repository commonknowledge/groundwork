from typing import Any, Dict, Generic, Iterable, Type, TypeVar

from abc import ABCMeta, abstractmethod

ResourceT = TypeVar("ResourceT")


class ExternalResource(Generic[ResourceT], metaclass=ABCMeta):
    """
    Abstract interface for reading from an external resource.

    For most REST APIs, unless you are wrapping an existing client library, you probably wanty to use the subclass `ApiClient` instead of this class.
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
