from typing import Any, Dict, Iterable, List, TypeVar

from pyck.core.datasource import ExternalResource

ResourceT = TypeVar("ResourceT")


class MockExternalResource(ExternalResource[ResourceT]):
    def __init__(
        self, data: List[ResourceT], primary_key: str = "id", **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self.data = data
        self.primary_key = primary_key

    def list(self, **kwargs: Any) -> Iterable[ResourceT]:
        return self.data

    def get(self, id: str) -> ResourceT:
        return next(x for x in self.data if getattr(x, self.primary_key) == id)
