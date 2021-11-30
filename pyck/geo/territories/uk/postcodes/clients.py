from typing import Any, Dict, TypeVar

from pyck.core.api_client import RestResource
from pyck.geo.territories.uk.postcodes import types

DataclassT = TypeVar("DataclassT")


class PostcodesApiResource(RestResource[DataclassT]):
    base_url = "https://api.postcodes.io"

    def _get(self, url: str, query: Dict[str, Any]) -> Any:
        res = super()._get(url, query)
        return res["result"]


postcode: PostcodesApiResource[types.GeolocatedPostcode] = PostcodesApiResource(
    path="/postcodes",
    dataclass=types.GeolocatedPostcode,
)
