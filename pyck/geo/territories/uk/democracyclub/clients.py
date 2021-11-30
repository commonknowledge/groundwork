from typing import Any, Dict, Optional, TypeVar

from pyck.core.api_client import RestResource
from pyck.geo.territories.uk.democracyclub import types

DataclassT = TypeVar("DataclassT")


class DemocracyClubApiResource(RestResource[DataclassT]):
    base_url = "https://candidates.democracyclub.org.uk/api/v0.9"

    def _list(self, **kwargs):
        kwargs.setdefault("page_size", 100)

        url = self.url
        query: Optional[Dict[str, Any]] = kwargs

        while url is not None:
            res = self._get(url, query)

            url = res["next"]
            query = None  # Is already appended to the 'next' url

            yield from res["results"]


election_result_set: DemocracyClubApiResource[
    types.ResultSet
] = DemocracyClubApiResource(path="/result_sets", dataclass=types.ResultSet)


elections: DemocracyClubApiResource[types.Election] = DemocracyClubApiResource(
    path="/elections",
    dataclass=types.Election,
)
