import os
from dataclasses import dataclass
from test.tags import integration_test

from django.conf import settings
from django.test import TestCase

from groundwork.contrib.airtable import datasources


@integration_test
class AirtableApiTests(TestCase):
    def setUp(self):
        self.datasource = datasources.AirtableDatasource(
            resource_type=MyResource,
            api_key=settings.EXAMPLE_AIRTABLE_API_KEY,
            base_id=settings.EXAMPLE_AIRTABLE_BASE,
            table_name="Table 1",
        )

    def test_can_paginate_list(self):
        self.assertListReturnsAtLeastCount(self.datasource, 120)

    def test_can_get(self):
        self.assertCanGetResourceReturnedFromList(self.datasource)

    def assertListReturnsAtLeastCount(self, resource_type, expected):
        results = list(resource_type.list())
        self.assertGreater(len(results), expected)

    def assertCanGetResourceReturnedFromList(self, resource_type):
        resource = next(resource_type.list())
        resource_type.get(resource_type.get_id(resource))


@dataclass
class MyResource:
    id: str
    name: str = datasources.airtable_field("Name")
    notes: str = datasources.airtable_field("Notes")
