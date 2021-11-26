from typing import Any, Dict, Optional, Type

from datetime import datetime, timedelta

from django.db import models

from pyck.core.datasource import ExternalResource


class SyncedModel(models.Model):
    class Meta:
        abstract = True

    sync_interval = timedelta(days=1)
    datasource: Type[ExternalResource]
    resource_property_mapping: Optional[Dict[str, str]] = None

    external_id = models.CharField(max_length=256)
    last_synced = models.DateTimeField()

    @classmethod
    def get_saved_properties(cls, resource):
        return resource

    @classmethod
    def sync(cls):
        field_set = {f.name for f in cls._meta.get_fields()}
        for item in cls.datasource.list():
            properties = {
                key: val
                for key, val in cls.get_saved_properties(item).items()
                if key in field_set
            }

            properties["last_synced"] = datetime.now()

            cls.objects.update_or_create(
                external_id=cls.datasource.get_external_id(item), defaults=properties
            )
