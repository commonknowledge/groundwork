from typing import Any, Dict, Iterable, Optional, TypeVar

import dataclasses

from django.conf import settings

from groundwork.core.datasources import RestDatasource

ResourceT = TypeVar("ResourceT")


def airtable_field(name: str, **kwargs):
    metadata = {__name__: {"airtable_field": name}}
    metadata.update(kwargs.pop("metadata", None) or {})

    return dataclasses.field(metadata=metadata, **kwargs)


class AirtableDatasource(RestDatasource[ResourceT]):
    base_url = "https://api.airtable.com/v0"
    api_key: str

    base_id: Optional[str] = None
    table_name: Optional[str] = None

    def get_headers(self) -> Dict[str, str]:
        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def __init__(self, resource_type: ResourceT, base=None, table=None, **kwargs):
        super().__init__(resource_type=resource_type, **kwargs)

        if not getattr(self, "path", None):
            assert self.base_id
            assert self.table_name
            self.path = f"/{self.base_id}/{self.table_name}"

        if not hasattr(self, "api_key"):
            self.api_key = getattr(settings, "AIRTABLE_API_KEY", None)

    def get_mapped_field_name(self, field):
        if __name__ not in field.metadata:
            return field.name

        return field.metadata[__name__]["airtable_field"]

    def get_mapped_field_value(
        self, field: dataclasses.Field, data: Dict[str, Any]
    ) -> Any:
        mapped_name = self.get_mapped_field_name(field)
        if mapped_name in data:
            return data[mapped_name]

        if field.type == bool:
            return False

        if field.type == str:
            return ""

        return None

    def paginate(self, **query: Dict[str, Any]) -> Iterable[ResourceT]:
        offset = None

        while True:
            if offset is not None:
                query["offset"] = offset
            data = self.fetch_url(self.url, query)

            yield from data["records"]

            offset = data.get("offset")
            if offset is None:
                return

    def deserialize(self, data: Dict[str, Any]) -> ResourceT:
        field_data = data["fields"]

        mapped_data = {
            field.name: self.get_mapped_field_value(field, field_data)
            for field in dataclasses.fields(self.resource_type)
        }
        mapped_data["id"] = data["id"]

        return super().deserialize(mapped_data)
