from typing import List, Optional

from dataclasses import dataclass
from datetime import date


@dataclass
class Person:
    id: int
    url: str
    name: str


@dataclass
class Party:
    id: str
    url: str


@dataclass
class Post:
    id: str
    url: str
    label: str
    slug: str


@dataclass
class OrganizationSummary:
    id: str
    url: str
    name: str


@dataclass
class ElectionSummary:
    id: str
    url: str
    name: str


@dataclass
class Membership:
    id: int
    url: str
    label: str
    role: str
    elected: bool
    person: Person
    on_behalf_of: Party
    post: Post
    election: ElectionSummary
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@dataclass
class CandidateResult:
    id: int
    url: str
    membership: Membership
    result_set: str
    num_ballots: int
    is_winner: bool


@dataclass
class Election:
    id: str
    url: str
    name: str
    winner_membership_role: str
    candidate_membership_role: str
    election_date: date
    current: bool
    use_for_candidate_suggestions: bool
    organization: OrganizationSummary
    party_lists_in_use: bool
    default_party_list_members_to_show: int
    show_official_documents: bool
    ocd_division: str
    description: str


@dataclass
class ResultSet:
    id: int
    url: str
    candidate_results: List[CandidateResult]
