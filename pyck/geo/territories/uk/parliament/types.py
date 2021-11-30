from typing import Optional

from dataclasses import dataclass, field
from datetime import datetime

from pyck.geo.territories.uk.parliament.serializers import embedded_value


@dataclass
class Party:
    id: int
    name: str
    abbreviation: str
    is_lords_main_party: bool
    is_lords_spiritual_party: bool
    is_independent_party: bool
    background_colour: Optional[str] = None
    government_type: Optional[int] = None
    foreground_colour: Optional[str] = None


@dataclass
class Representation:
    # Stub definition.
    membership_from_id: int


@dataclass
class Member:
    name_list_as: str
    name_display_as: str
    name_full_title: str
    latest_party: Party
    gender: str
    thumbnail_url: str
    latest_house_membership: Representation
    name_address_as: Optional[str] = None


@dataclass
class CurrentRepresentation:
    representation: Representation
    member: Member = embedded_value(Member)


@dataclass
class Constituency:
    id: int
    name: str
    start_date: datetime
    ons_code: str
    end_date: Optional[datetime] = None
    current_representation: Optional[CurrentRepresentation] = None
