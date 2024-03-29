from test.tags import integration_test

from django.test import TestCase

from groundwork.geo.territories.uk import postcodes


@integration_test
class PostcodesIOApiTests(TestCase):
    def test_geocodes_postcode(self):
        for example in self.EXAMPLE_POSTCODES:
            expected = self.to_value_type(**example)
            result = postcodes.postcode.get(example["postcode"])
            self.assertEqual(result.postcode, expected.postcode)

    def to_value_type(self, codes, **kwargs):
        return postcodes.GeolocatedPostcode(codes=postcodes.OnsCodes(**codes), **kwargs)

    EXAMPLE_POSTCODES = [
        {
            "postcode": "OX49 5NU",
            "quality": 1,
            "eastings": 464438,
            "northings": 195677,
            "country": "England",
            "nhs_ha": "South Central",
            "longitude": -1.069876,
            "latitude": 51.6562,
            "primary_care_trust": "Oxfordshire",
            "region": "South East",
            "lsoa": "South Oxfordshire 011B",
            "msoa": "South Oxfordshire 011",
            "incode": "5NU",
            "outcode": "OX49",
            "parliamentary_constituency": "Henley",
            "admin_district": "South Oxfordshire",
            "parish": "Brightwell Baldwin",
            "admin_county": "Oxfordshire",
            "admin_ward": "Chalgrove",
            "ced": "Chalgrove and Watlington",
            "ccg": "NHS Oxfordshire",
            "nuts": "Oxfordshire CC",
            "codes": {
                "admin_district": "E07000179",
                "admin_county": "E10000025",
                "admin_ward": "E05009735",
                "parish": "E04008109",
                "parliamentary_constituency": "E14000742",
                "ccg": "E38000136",
                "ccg_id": "10Q",
                "ced": "E58001732",
                "nuts": "TLJ14",
                "lsoa": "E01028601",
                "msoa": "E02005968",
                "lau2": "E07000179",
            },
        },
        {
            "postcode": "M32 0JG",
            "quality": 1,
            "eastings": 379988,
            "northings": 395476,
            "country": "England",
            "nhs_ha": "North West",
            "longitude": -2.302836,
            "latitude": 53.455654,
            "primary_care_trust": "Trafford",
            "region": "North West",
            "lsoa": "Trafford 003C",
            "msoa": "Trafford 003",
            "incode": "0JG",
            "outcode": "M32",
            "parliamentary_constituency": "Stretford and Urmston",
            "admin_district": "Trafford",
            "parish": "Trafford, unparished area",
            "admin_county": None,
            "admin_ward": "Gorse Hill",
            "ced": None,
            "ccg": "NHS Trafford",
            "nuts": "Greater Manchester South West",
            "codes": {
                "admin_district": "E08000009",
                "admin_county": "E99999999",
                "admin_ward": "E05000829",
                "parish": "E43000163",
                "parliamentary_constituency": "E14000979",
                "ccg": "E38000187",
                "ccg_id": "02A",
                "ced": "E99999999",
                "nuts": "TLD34",
                "lsoa": "E01006187",
                "msoa": "E02001261",
                "lau2": "E08000009",
            },
        },
        {
            "postcode": "NE30 1DP",
            "quality": 1,
            "eastings": 435958,
            "northings": 568671,
            "country": "England",
            "nhs_ha": "North East",
            "longitude": -1.439269,
            "latitude": 55.011303,
            "primary_care_trust": "North Tyneside",
            "region": "North East",
            "lsoa": "North Tyneside 016C",
            "msoa": "North Tyneside 016",
            "incode": "1DP",
            "outcode": "NE30",
            "parliamentary_constituency": "Tynemouth",
            "admin_district": "North Tyneside",
            "parish": "North Tyneside, unparished area",
            "admin_county": None,
            "admin_ward": "Tynemouth",
            "ced": None,
            "ccg": "NHS North Tyneside",
            "nuts": "Tyneside",
            "codes": {
                "admin_district": "E08000022",
                "admin_county": "E99999999",
                "admin_ward": "E05001130",
                "parish": "E43000176",
                "parliamentary_constituency": "E14001006",
                "ccg": "E38000127",
                "ccg_id": "99C",
                "ced": "E99999999",
                "nuts": "TLC22",
                "lsoa": "E01008561",
                "msoa": "E02001753",
                "lau2": "E08000022",
            },
        },
    ]
