from typing import Any, Dict, Optional

from pyck.core.api_client import ApiClient
from pyck.geo.territories.uk.democracyclub import serializers


class DemocracyClubApiClient(ApiClient):
    def list(self, **kwargs):
        kwargs.setdefault("page_size", 100)

        url = self.url
        query: Optional[Dict[str, Any]] = kwargs

        while url is not None:
            res = self._get(url, **query)

            url = res["next"]
            query = None  # Is already appended to the 'next' url

            for item in res["results"]:
                yield self._deserialize(item)


election_result_sets = DemocracyClubApiClient(
    url="https://candidates.democracyclub.org.uk/api/v0.9/result_sets",
    serializer_class=serializers.ResultSetSerializer,
)


elections = DemocracyClubApiClient(
    url="https://candidates.democracyclub.org.uk/api/v0.9/elections",
    serializer_class=serializers.ElectionSerializer,
)
