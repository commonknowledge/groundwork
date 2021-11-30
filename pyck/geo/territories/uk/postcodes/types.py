from typing import Optional

from dataclasses import dataclass

from django.contrib.gis.geos import Point


@dataclass
class OnsCodes:
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
        return Point(self.longitude, self.latitude, srid=4326)
