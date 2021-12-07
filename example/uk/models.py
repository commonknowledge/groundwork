from django.db import models

from pyck.core.datasources import SyncConfig, SyncedModel
from pyck.geo.territories.uk import parliament


class Constituency(SyncedModel):
    sync_config = SyncConfig(
        datasource=parliament.constituencies,
    )

    external_id = models.IntegerField()
    name = models.CharField(max_length=512)
    ons_code = models.CharField(max_length=512)
    current_mp = models.ForeignKey("MP", null=True, on_delete=models.SET_NULL)


class MP(SyncedModel):
    sync_config = SyncConfig(datasource=parliament.members, sync_interval=None)

    external_id = models.IntegerField()
    name_display_as = models.CharField(max_length=512)
    thumbnail_url = models.URLField(max_length=512)
    latest_party = models.ForeignKey("Party", null=True, on_delete=models.SET_NULL)


class Party(SyncedModel):
    sync_config = SyncConfig(datasource=parliament.parties, sync_interval=None)

    external_id = models.IntegerField()
    name = models.CharField(max_length=512)
    foreground_colour = models.CharField(max_length=16, null=True)
    background_colour = models.CharField(max_length=16, null=True)
