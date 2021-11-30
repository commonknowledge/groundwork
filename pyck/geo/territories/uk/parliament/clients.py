from typing import Any, Dict, Optional, TypeVar

from djangorestframework_camel_case.parser import CamelCaseJSONParser

from pyck.core.api_client import RestResource
from pyck.core.cache import django_cached
from pyck.geo.territories.uk import ons
from pyck.geo.territories.uk.parliament import types

DataclassT = TypeVar("DataclassT")


class ParliamentApiResource(RestResource[DataclassT]):
    parser_class = CamelCaseJSONParser
    base_url = "https://members-api.parliament.uk/api"

    def _list(self, **kwargs):
        # We use the search api for 'list' operations. A search query  must be provided, otherwise no results are
        # returned
        kwargs.setdefault("searchText", "")
        url = self.url + "/Search"

        i = 0

        while True:
            res = self._get(url, kwargs)

            for item in res["items"]:
                yield item["value"]
                i += 1

            kwargs["skip"] = i
            if i >= res["total_results"]:
                return


class _ParliamentConstituenciesResource(ParliamentApiResource[types.Constituency]):
    """
    Augments the constituency api response with the ONS code for the constituency, as this is not provided by the
    parliament API by default and is widely required for matching to geographical locations.
    """

    path = "/Location/Constituency"

    def _deserialize(self, data: Any) -> Any:
        ons_lookup = self.get_ons_code_lookup()
        constituency_name = data["name"].lower()

        data["ons_code"] = ons_lookup[constituency_name]
        return super()._deserialize(data)

    @django_cached(__name__ + ".ons_code_lookup")
    def get_ons_code_lookup(self):
        # Retreive constituency codes mapped to official constituency name. This is the only common identifier shared
        # by ons and parliament APIs. Although not the most robust imaginable way of doing this, we figure it is better
        # for this to fail fast in a list operation (typically in a batch job) rather than failing later
        # (typically in response to a user request)

        return {
            ons_code.label.lower(): ons_code.code
            for ons_code in ons.constituency_codes.list()
        }


constituencies: RestResource[types.Constituency] = _ParliamentConstituenciesResource(
    dataclass=types.Constituency
)
