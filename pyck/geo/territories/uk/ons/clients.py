from typing import TypeVar

from pyck.core.api_client import RestResource
from pyck.geo.territories.uk.ons import types

DataclassT = TypeVar("DataclassT")


class ONSApiResource(RestResource[DataclassT]):
    base_url = "https://api.beta.ons.gov.uk/v1"

    def _list(self, **kwargs):
        kwargs.setdefault("limit", 100)

        i = 0

        while True:
            res = self._get(self.url, kwargs)

            for item in res["items"]:
                yield item
                i += 1

            if i >= res["total_count"]:
                return

            kwargs["offset"] = i


constituency_codes: ONSApiResource[types.OnsCode] = ONSApiResource(
    path="/code-lists/parliamentary-constituencies/editions/one-off/codes",
    dataclass=types.OnsCode,
    filter=lambda item: item.is_westminster_constituency,
)
