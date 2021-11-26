from datetime import date, timedelta

from pyck.core.datasource import ExternalResource
from pyck.geo.territories.uk import democracyclub


class ParliamentryConstituencyResource(ExternalResource):
    def list(self):
        last_relevant_election_date = date.today() - timedelta(years=5)

        relevant_parliamentry_elections = (
            election
            for election in democracyclub.elections.list()
            if election["election_date"] >= last_relevant_election_date
            and election["organization"]["id"] == "parl:parl"
        )

        for election in sorted(
            relevant_parliamentry_elections, key=lambda x: x["election_date"]
        ):
            result_set = democracyclub.election_result_sets.get(election["url"])
