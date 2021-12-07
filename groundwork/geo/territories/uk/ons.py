from typing import TypeVar

from dataclasses import dataclass

from groundwork.core.datasources import RestDatasource


class OnsCodeType:
    WESTMINSTER_CONSTITUENCY_ENGLAND = "E14"
    WESTMINSTER_CONSTITUENCY_WALES = "W07"
    WESTMINSTER_CONSTITUENCY_SCOTLAND = "S14"
    WESTMINSTER_CONSTITUENCY_NI = "N06"


@dataclass
class OnsCode:
    code: str
    label: str

    def is_type(self, *types: str) -> bool:
        return next((True for t in types if self.code.startswith(t)), False)

    @property
    def is_westminster_constituency(self) -> bool:
        return self.is_type(
            OnsCodeType.WESTMINSTER_CONSTITUENCY_ENGLAND,
            OnsCodeType.WESTMINSTER_CONSTITUENCY_WALES,
            OnsCodeType.WESTMINSTER_CONSTITUENCY_SCOTLAND,
            OnsCodeType.WESTMINSTER_CONSTITUENCY_NI,
        )


ResourceT = TypeVar("ResourceT")


class _ONSApiDatasource(RestDatasource[ResourceT]):
    base_url = "https://api.beta.ons.gov.uk/v1"

    def paginate(self, **kwargs):
        kwargs.setdefault("limit", 100)

        i = 0

        while True:
            res = self.fetch_url(self.url, kwargs)

            for item in res["items"]:
                yield item
                i += 1

            if i >= res["total_count"]:
                return

            kwargs["offset"] = i


constituency_codes: RestDatasource[OnsCode] = _ONSApiDatasource(
    path="/code-lists/parliamentary-constituencies/editions/one-off/codes",
    resource_type=OnsCode,
    filter=lambda item: item.is_westminster_constituency,
)
"""
Looks up ONS constituency resources mapping the official constituency name to its ONS code.

This is primarily used internally to clean data returned by APIs that don't provide ONS codes.
"""
