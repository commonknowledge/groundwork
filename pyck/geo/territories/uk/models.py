from django.db import models

from pyck.core.models import SyncedModel
from pyck.geo.territories.uk.resources import UKParliamentryConstituencyResource


class ParliamentryConstituency(SyncedModel):
    datasource = UKParliamentryConstituencyResource

    name = models.CharField(max_length=1024)
    ons_id = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    current_representation = models.ForeignKey(
        "MemberOfParliament", null=True, blank=True, on_delete=models.SET_NULL
    )


class PoliticalParty(SyncedModel):
    datasource = UKParliamentryConstituencyResource

    name = models.CharField(max_length=1024)
    ons_id = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)


class MemberOfParliament(SyncedModel):
    datasource = UKParliamentryConstituencyResource

    name = models.CharField(max_length=1024)
    ons_id = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
