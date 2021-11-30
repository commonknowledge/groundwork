from typing import Any, List

from dataclasses import dataclass
from test.core.mocks import MockExternalResource

from django.db import models
from django.test import TestCase

from pyck.core.datasource import ExternalResource
from pyck.core.models import SyncedModel


@dataclass
class ExampleResource:
    id: str
    name: str
    age: int
    teacher: str
    friends: List[str]


class ExampleSyncedModel(SyncedModel):
    class SyncConfig:
        external_id = "external_id"

        field_map = {
            "external_id": "id",
            "name": "name",
            "mentor": "teacher",
            "comrades": "friends",
        }

        datasource = MockExternalResource(
            [
                ExampleResource(
                    id="alice",
                    name="Alice",
                    age=56,
                    teacher="bob",
                    friends=["bob", "arlo"],
                ),
                ExampleResource(
                    id="bob", name="Bob", age=44, teacher="alice", friends=["alice"]
                ),
                ExampleResource(
                    id="arlo",
                    name="Arlo",
                    age=76,
                    teacher="alice",
                    friends=["alice", "woody"],
                ),
                ExampleResource(
                    id="woody", name="Woody", age=102, teacher="arlo", friends=["arlo"]
                ),
            ]
        )

    external_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    mentor = models.ForeignKey(
        "ExampleSyncedModel", related_name="mentor_of", on_delete=models.CASCADE
    )
    comrades = models.ManyToManyField("ExampleSyncedModel")


class SyncedModelTestCase(TestCase):
    def test_sync(self):
        ExampleSyncedModel.sync()

        for source_item in ExampleSyncedModel.SyncConfig.datasource.data:
            local_copy = ExampleSyncedModel.objects.get(external_id=source_item.id)

            expected_local_copy = ExampleSyncedModel(
                id=local_copy.id,
                name=source_item.name,
                mentor=ExampleSyncedModel.objects.get(external_id=source_item.teacher),
            )

            self.assertEqual(
                local_copy, expected_local_copy, "Sets mapped properties on local copy"
            )

            expected_linked_ids = {
                ExampleSyncedModel.objects.get(external_id=item).id
                for item in source_item.friends
            }
            linked_ids = {c.id for c in local_copy.comrades.all()}

            self.assertEqual(
                linked_ids, expected_linked_ids, "Links to relationships on local copy"
            )

    def test_syncs_multiple_times_without_error(self):
        ExampleSyncedModel.sync()
        ExampleSyncedModel.sync()
