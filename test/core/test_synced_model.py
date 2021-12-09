from typing import Any, List, Optional

from dataclasses import dataclass, field

from django.db import models
from django.test import TestCase

from groundwork.core.datasources import MockDatasource, SyncConfig, SyncedModel


class SyncedModelTestCase(TestCase):
    def setUp(self) -> None:
        SomeSyncedModel.sync_config = SomeSyncedModel.initial_config()
        SomeRelatedModel.sync_config = SomeRelatedModel.initial_config()

    def test_handles_sync_with_all_optional_fields_provided(self):
        SomeSyncedModel.sync_config.datasource.data = [
            SomeResource(
                id="1",
                required_value="Required 1",
                optional_value="Optional 1",
                optional_relationship="1",
                required_relationship="1",
            ),
            SomeResource(
                id="2",
                required_value="Required 2",
                optional_value="Optional 2",
                optional_relationship="2",
                required_relationship="2",
            ),
        ]
        SomeRelatedModel.sync_config.datasource.data = [
            SomeResource(
                id="1",
            ),
            SomeResource(
                id="2",
            ),
        ]

        SomeSyncedModel.sync()

        self.assertModelCount(SomeSyncedModel, 2)
        self.assertModelCount(SomeRelatedModel, 2)

        self.assertModelExists(
            SomeSyncedModel,
            external_id="1",
            required_value="Required 1",
            optional_value="Optional 1",
            optional_relationship__external_id="1",
            required_relationship__external_id="1",
        )

        self.assertModelExists(
            SomeSyncedModel,
            external_id="2",
            required_value="Required 2",
            optional_value="Optional 2",
            optional_relationship__external_id="2",
            required_relationship__external_id="2",
        )

    def test_handles_sync_with_no_optional_fields_provided(self):
        SomeSyncedModel.sync_config.datasource.data = [
            SomeResource(
                id="1",
                required_value="Required 1",
            ),
            SomeResource(
                id="2",
                required_value="Required 2",
            ),
        ]
        SomeRelatedModel.sync_config.datasource.data = [
            SomeResource(
                id="1",
            )
        ]

        SomeSyncedModel.sync()

        self.assertModelCount(SomeSyncedModel, 2)

        self.assertModelExists(
            SomeSyncedModel,
            external_id="1",
            required_value="Required 1",
        )

        self.assertModelExists(
            SomeSyncedModel,
            external_id="2",
            required_value="Required 2",
        )

    def test_handles_sync_with_mapped_fields(self):
        @dataclass
        class MappedResource(SomeResource):
            required_value_mapped: str = ""
            required_relationship_mapped: str = ""

        SomeSyncedModel.sync_config.field_map = {
            "required_value": "required_value_mapped",
            "required_relationship": "required_relationship_mapped",
        }

        SomeSyncedModel.sync_config.datasource.data = [
            MappedResource(
                id="1",
                required_value_mapped="Required 1",
                required_relationship_mapped="1",
            ),
            MappedResource(
                id="2",
                required_value_mapped="Required 2",
                required_relationship_mapped="1",
            ),
        ]
        SomeRelatedModel.sync_config.datasource.data = [
            SomeResource(
                id="1",
            )
        ]

        SomeSyncedModel.sync()

        self.assertModelCount(SomeSyncedModel, 2)

        self.assertModelExists(
            SomeSyncedModel,
            external_id="1",
            required_value="Required 1",
        )

        self.assertModelExists(
            SomeSyncedModel,
            external_id="2",
            required_value="Required 2",
        )

    def test_handles_m2m_relationships(self):
        SomeSyncedModel.sync_config.datasource.data = [
            SomeResource(id="1", m2m_relationship=["1", "2"]),
        ]
        SomeRelatedModel.sync_config.datasource.data = [
            SomeResource(
                id="1",
            ),
            SomeResource(
                id="2",
            ),
        ]

        SomeSyncedModel.sync()

        self.assertModelCount(SomeSyncedModel, 1)
        self.assertModelCount(SomeRelatedModel, 2)

        self.assertModelExists(
            SomeRelatedModel, external_id="1", m2m_of__external_id="1"
        )
        self.assertModelExists(
            SomeRelatedModel, external_id="2", m2m_of__external_id="1"
        )

    def test_handles_recursive_relationships(self):
        SomeSyncedModel.sync_config.datasource.data = [
            SomeResource(id="1", recursive_relationship="1"),
            SomeResource(id="2", recursive_relationship="1"),
        ]

        SomeSyncedModel.sync()

        self.assertModelCount(SomeSyncedModel, 2)

        self.assertModelExists(
            SomeSyncedModel, external_id="1", recursive_relationship__external_id="1"
        )

        self.assertModelExists(
            SomeSyncedModel, external_id="2", recursive_relationship__external_id="1"
        )

    def test_handles_embedded_relationships(self):
        SomeSyncedModel.sync_config.datasource.data = [
            SomeResource(
                id="1",
                optional_relationship="1",
                required_relationship=SomeRelatedResource(id="2"),
                m2m_relationship=[SomeRelatedResource(id="3")],
            )
        ]

        SomeSyncedModel.sync()

        self.assertModelCount(SomeSyncedModel, 1)
        self.assertModelCount(SomeRelatedModel, 3)

        self.assertModelExists(
            SomeRelatedModel, external_id="2", required_of__external_id="1"
        )

        self.assertModelExists(
            SomeRelatedModel, external_id="3", m2m_of__external_id="1"
        )

    def test_syncs_multiple_times_without_error(self):
        SomeSyncedModel.sync()
        SomeSyncedModel.sync()

    def assertModelCount(self, model, count, **kwargs):
        self.assertEqual(model.objects.filter(**kwargs).count(), count)

    def assertModelExists(self, model, **kwargs):
        self.assertModelCount(model, 1, **kwargs)


@dataclass
class SomeResource:
    id: str
    required_value: str = "some_value"
    required_relationship: str = "1"
    m2m_relationship: List[Any] = field(default_factory=list)
    optional_value: Optional[Any] = None
    optional_relationship: Optional[Any] = None
    recursive_relationship: Optional[Any] = None


@dataclass
class SomeRelatedResource:
    id: str
    value: str = "some_value"


class SomeSyncedModel(SyncedModel):
    @staticmethod
    def initial_config():
        return SyncConfig(datasource=MockDatasource([SomeResource(id="1")]))

    sync_config = SyncConfig(datasource=MockDatasource([]))

    external_id = models.CharField(max_length=128)

    required_value = models.CharField(max_length=128)
    optional_value = models.CharField(max_length=128, null=True)

    optional_relationship = models.ForeignKey(
        "SomeRelatedModel",
        null=True,
        related_name="optional_of",
        on_delete=models.CASCADE,
    )
    required_relationship = models.ForeignKey(
        "SomeRelatedModel",
        related_name="required_of",
        on_delete=models.CASCADE,
    )
    recursive_relationship = models.ForeignKey(
        "SomeSyncedModel",
        null=True,
        related_name="recursive_of",
        on_delete=models.CASCADE,
    )
    m2m_relationship = models.ManyToManyField("SomeRelatedModel", related_name="m2m_of")
    embedded = models.ForeignKey(
        "SomeRelatedModel", null=True, on_delete=models.SET_NULL
    )


class SomeRelatedModel(SyncedModel):
    @staticmethod
    def initial_config():
        return SyncConfig(
            datasource=MockDatasource([SomeResource(id="1")]),
            sync_interval=None,
        )

    sync_config = SyncConfig(datasource=MockDatasource([]))

    external_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
