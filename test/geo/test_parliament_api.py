from test.tags import integration_test

from django.test import TestCase

from groundwork.geo.territories.uk import parliament


@integration_test
class ParliamentApiTests(TestCase):
    def test_returns_constituencies(self):
        self.assertListReturnsAtLeastCount(parliament.constituencies, 300)
        self.assertCanGetResourceReturnedFromList(parliament.constituencies)

    def test_returns_members(self):
        self.assertListReturnsAtLeastCount(parliament.members, 300)
        self.assertCanGetResourceReturnedFromList(parliament.members)

    def test_returns_parties(self):
        self.assertListReturnsAtLeastCount(parliament.parties, 4)
        self.assertCanGetResourceReturnedFromList(parliament.parties)

    def assertListReturnsAtLeastCount(self, resource_type, expected):
        results = list(resource_type.list())
        self.assertGreater(len(results), expected)

    def assertCanGetResourceReturnedFromList(self, resource_type):
        resource = next(resource_type.list())
        resource_type.get(resource_type.get_id(resource))
