from typing import Any, Dict, Optional, TypeVar

from dataclasses import dataclass

from django.contrib.gis.geos import Point

from groundwork.core.datasources import RestDatasource


@dataclass
class OnsCodes:
    """
    ONS Codes for UK governmental boundaries a postcode falls within.
    """

    admin_district: str
    admin_county: str
    admin_ward: str
    parish: str
    parliamentary_constituency: str
    ccg: str
    ccg_id: str
    ced: str
    nuts: str
    lsoa: str
    msoa: str
    lau2: str


@dataclass
class GeolocatedPostcode:
    """
    Metadata about a geolocated postcode.
    """

    postcode: str
    quality: int
    eastings: int
    northings: int
    country: str
    nhs_ha: str
    longitude: float
    latitude: float
    primary_care_trust: str
    region: str
    lsoa: str
    msoa: str
    incode: str
    outcode: str
    parliamentary_constituency: str
    admin_county: Optional[str]
    admin_district: str
    parish: str
    admin_ward: str
    ced: Optional[str]
    ccg: str
    nuts: str
    codes: OnsCodes

    def to_point(self):
        """
        Representation of this postcode's geolocation as a [Django GIS](https://docs.djangoproject.com/en/3.2/ref/contrib/gis/)-compatible point.

        Returns:
            A Django-GIS Point representing the postcode
        """
        return Point(self.longitude, self.latitude, srid=4326)


ResourceT = TypeVar("ResourceT")


class _PostcodesApiDatasource(RestDatasource[ResourceT]):
    base_url = "https://api.postcodes.io"

    def fetch_url(self, url: str, query: Dict[str, Any]) -> Any:
        res = super().fetch_url(url, query)
        return res["result"]


postcode: RestDatasource[GeolocatedPostcode] = _PostcodesApiDatasource(
    path="/postcodes",
    resource_type=GeolocatedPostcode,
)
"""
Geolocated postcode API resource.

Only GET requests are supported.

__`get(postcode)`:__

    Geocodes `postcode` and returns a `GeolocatedPostcode` instance.
"""
