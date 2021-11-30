from typing import Any, Dict, Optional

import uuid
from datetime import timedelta

from django.db import models
from django.db.models.fields import Field

from pyck.core.cron import register_cron
from pyck.core.datasource import ExternalResource
from pyck.core.internal.class_util import get_immediate_superclass, mixin_classes


class SyncedModel(models.Model):
    """
    Base class for models stored locally that are fetched on a schedule from a remote data source.
    """

    class Meta:
        abstract = True

    class SyncConfig:
        """
        Field on both the external resource and this model that is used to map values returned from the external service
        onto instances of the model.
        """

        external_id: str = "id"

        """
        Map from fields in the model to fields in the external resource.
        """
        field_map: Optional[Dict[str, str]] = None

        """
        Frequency with which the model should be synced from the external source
        """
        sync_interval = timedelta(days=1)

        """
        External resource to periodically sync this model with
        """
        datasource: ExternalResource[Any]

    """
    Last time this resource was updated from the remote resource.
    """
    last_sync_time = models.DateTimeField()

    """
    SyncedModels need to have a uuid primary key to handle recursive references when syncing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        # Merge the sync config with the superclass sync config.
        if cls != SyncedModel:
            cls.SyncConfig = mixin_classes(
                cls.SyncConfig, get_immediate_superclass(cls).SyncConfig
            )

        # Validate the SyncConfig
        if not cls.Meta.abstract and not hasattr(cls.SyncConfig, "datasource"):
            raise TypeError(
                "Subclasses of SyncedModel must define SyncConfig.datasource"
            )

        # Register the subclass with the cron manager
        if not cls.Meta.abstract:
            register_cron(cls.sync, cls.SyncConfig.sync_interval)

    @classmethod
    def get_datasource_field_key(cls, model_key: str) -> Optional[str]:
        if cls.SyncConfig.field_map is None:
            return model_key

        return cls.SyncConfig.field_map.get(model_key)

    @classmethod
    def sync(cls):
        from pyck.core.datasource.sync_manager import SyncManager

        SyncManager().sync_model(cls)
