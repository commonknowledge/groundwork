from typing import Any, Dict, Optional, TypeVar, cast

import re
from dataclasses import dataclass, field
from datetime import datetime

from djangorestframework_camel_case.parser import CamelCaseJSONParser

from groundwork.core.cache import django_cached
from groundwork.core.datasources import RestDatasource
from groundwork.geo.territories.uk import ons
from groundwork.geo.territories.uk.internal.serializers import embedded_value

# https://members-api.parliament.uk/index.html


@dataclass
class Party:
    """
    Represent a political party
    """

    id: int
    name: str
    is_lords_main_party: bool
    is_lords_spiritual_party: bool
    is_independent_party: bool
    abbreviation: Optional[str] = None
    background_colour: Optional[str] = None
    government_type: Optional[int] = None
    foreground_colour: Optional[str] = None


@dataclass
class Representation:
    """
    Represent an MP's period of representation in parliament.
    """

    # Stub definition.
    membership_from_id: Optional[int] = None


@dataclass
class Member:
    """
    Represent an MP.
    """

    id: int
    name_list_as: str
    name_display_as: str
    name_full_title: str
    gender: str
    thumbnail_url: str
    latest_house_membership: Representation
    latest_party: Optional[Party] = None
    name_address_as: Optional[str] = None


@dataclass
class CurrentRepresentation:
    """
    Represent a current MP.
    """

    representation: Representation
    member: Member = embedded_value(Member)


@dataclass
class Constituency:
    """
    Represent a Westminster constituency.
    """

    id: int
    name: str
    start_date: datetime
    ons_code: str
    end_date: Optional[datetime] = None
    current_representation: Optional[CurrentRepresentation] = None

    @property
    def current_mp(self) -> Optional[Member]:
        if self.current_representation:
            return self.current_representation.member
        else:
            return None


ResourceT = TypeVar("ResourceT")


class _ParliamentApiDatasource(RestDatasource[ResourceT]):
    parser_class = CamelCaseJSONParser
    base_url = "https://members-api.parliament.uk/api"
    list_suffix = "/Search"

    def flatten_resource(self, data: Any) -> Any:
        if set(data.keys()) == {"value", "links"}:
            data = data["value"]

        return data

    def deserialize(self, data: Any) -> ResourceT:
        return super().deserialize(self.flatten_resource(data))

    def paginate(self, **kwargs):
        # We use the search API for 'list' operations. A search query  must be provided, otherwise no results are
        # returned
        kwargs.setdefault("searchText", "")
        url = self.url + self.list_suffix

        i = 0

        while True:
            res = self.fetch_url(url, kwargs)

            for item in res["items"]:
                yield item["value"]
                i += 1

            kwargs["skip"] = i
            if i >= res["total_results"]:
                return


class _ParliamentSmallListApiDatasource(_ParliamentApiDatasource[ResourceT]):
    """
    Adapt resources that only return a small number of responses and therefore don't support a get()
    method.
    """

    list_suffix = ""

    def get(self, id: str, **kwargs: Dict[str, Any]) -> ResourceT:
        return cast(ResourceT, next(x for x in self.list() if self.get_id(x) == id))


class _ParliamentConstituenciesDatasource(_ParliamentApiDatasource[Constituency]):
    """
    Augments the constituency API response with the ONS code for the constituency, as this is not provided by the
    parliament API by default and is widely required for matching to geographical locations.
    """

    path = "/Location/Constituency"

    def deserialize(self, data: Any) -> Any:
        data = self.flatten_resource(data)
        ons_lookup = self.get_ons_code_lookup()
        constituency_name = data["name"].lower()

        data["ons_code"] = ons_lookup[constituency_name]
        return super().deserialize(data)

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


constituencies: RestDatasource[Constituency] = _ParliamentConstituenciesDatasource(
    resource_type=Constituency
)
"""
Resource returning all current UK constituencies, along with their current representation in parliament.
"""


members: RestDatasource[Member] = _ParliamentApiDatasource(
    path="/Members",
    resource_type=Member,
)
"""
Resource returning all current UK MPs, along with their current representation in parliament.
"""


parties: RestDatasource[Party] = _ParliamentSmallListApiDatasource(
    path="/Parties/GetActive/Commons", resource_type=Party
)
"""
Resource returning all current UK political parties represented in Westminster
"""
