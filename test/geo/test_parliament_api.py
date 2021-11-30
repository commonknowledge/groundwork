from django.test import TestCase

from pyck.geo.territories.uk import parliament


class ParliamentApiTests(TestCase):
    def test_returns_constituencies(self):
        result = list(parliament.constituencies.list())

        self.assertGreater(len(result), 300, "Returns a list of constituencies")
