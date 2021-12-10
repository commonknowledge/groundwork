from typing import Any, Dict, Iterable, Optional, TypeVar

import dataclasses

from django.conf import settings
from rest_framework_dataclasses.field_utils import get_type_info

from groundwork.core.datasources import RestDatasource

ResourceT = TypeVar("ResourceT")


def airtable_field(name: str, **kwargs: Dict[str, Any]) -> dataclasses.Field:
    """
    Return a [dataclass field](https://docs.python.org/3/library/dataclasses.html#dataclasses.Field) used to annotate
    a Resource class with the name of the column in Airtable.

    For example, if you have an Airtable like this:

    | First Name  | Last Name  |
    | ----------- | ---------- |
    | Stafford    | Beer       |
    | Clara       | Zetkin     |

    You could map it onto a django model like this:

    ```python
    @dataclass
    class People:
        id: str
        first_name: str = airtable_field('First Name')
        last_name: str = airtable_field('Last Name')
    ```

    If you do not annotate your field like this, `AirtableDatasource` will expect your column in Airtable to have the
    same name as your Resource class.

    Args:
        name: Airtable column name associated with this field.
        kwargs: Keyword args passed to [dataclasses.field](https://docs.python.org/3/library/dataclasses.html#dataclasses.field).

    Returns:
        A dataclass field descriptor identifying the corresponding Airtable column.

    """
    metadata = {__name__: {"airtable_field": name}}
    metadata.update(kwargs.pop("metadata", None) or {})

    return dataclasses.field(metadata=metadata, **kwargs)


class AirtableDatasource(RestDatasource[ResourceT]):
    """
    Base class for implementing clients to Airtable bases and converting their responses to resource objects.

    You are encouraged to use Python's inbuilt [`@dataclass`](https://docs.python.org/3/library/dataclasses.html)
    decorator and define type hints when defining these classes as this allows type-safe serializers to be
    auto-generated and decreases the amount of boilerplate code that you need to write.

    __Example:__

    Let's assume we have a public airtable with the base id `4rQYK6P56My`. It contains a table called 'Active Members',
    which looks like this:

    | First Name  | Last Name  |
    | ----------- | ---------- |
    | Stafford    | Beer       |
    | Clara       | Zetkin     |


    We can create a datasource for it as follows:

    ```python
    from dataclasses import dataclass
    from groundwork.contrib.airtable.datasources import AirtableDatasource, airtable_field

    @dataclass
    class Person:
        id: str
        first_name: str = airtable_field('First Name')
        last_name: str = airtable_field('Last Name')

    my_datasource = AirtableDatasource(
        base_id="4rQYK6P56My",
        table_name="Active Members",
        resource_class=Person,
    )
    ```

    As with other datasource types, configuration can all either be provided as keyword-args to the constructor, or
    overridden in subclasses.
    """

    base_url = "https://api.airtable.com/v0"

    api_key: str
    """
    Airtable API key. Required for private Airtable bases. If not defined, will default to the value of
    `django.conf.settings.AIRTABLE_API_KEY`.
    """

    base_id: Optional[str] = None
    """
    ID of the airtable base. You can find this in your base's [API Docs](https://airtable.com/api)
    """

    table_name: Optional[str] = None
    """
    Name of the table to fetch from.
    """

    def __init__(self, resource_type: ResourceT, base=None, table=None, **kwargs):
        super().__init__(resource_type=resource_type, **kwargs)

        if not getattr(self, "path", None):
            assert self.base_id
            assert self.table_name
            self.path = f"/{self.base_id}/{self.table_name}"

        if not hasattr(self, "api_key"):
            self.api_key = getattr(settings, "AIRTABLE_API_KEY", None)

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
            field.name: self._get_mapped_field_value(field, field_data)
            for field in dataclasses.fields(self.resource_type)
        }
        mapped_data["id"] = data["id"]

        return super().deserialize(mapped_data)

    def get_headers(self) -> Dict[str, str]:
        headers = {}

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def _get_mapped_field_name(self, field: dataclasses.Field) -> str:
        """
        Look up the mapped field name expected from the Airtable response.

        Args:
            field: Dataclass field descriptor for the resource field

        Returns:
            Airtable column name defined in the field's metadata. Returns the field name if none found,
        """

        if __name__ not in field.metadata:
            return field.name

        return field.metadata[__name__]["airtable_field"]

    def _get_mapped_field_value(
        self, field: dataclasses.Field, data: Dict[str, Any]
    ) -> Any:
        """
        Handle the fact that Airtable omits fields for 'falsy' values. Use the field metadata to determine if we have
        a type supporting a 'falsy' value and return it if missing from the airtable response.

        Args:
            field: Dataclass field descriptor for the resource field.
            data: The raw json object containing field values returned by Airtable.

        Returns:
            The value in `data` identified by `field`, with the appropriate 'falsy' value substituted for missing values
            if relevant to the field type.
        """

        mapped_name = self._get_mapped_field_name(field)
        if mapped_name in data:
            return data[mapped_name]

        type_info = get_type_info(field.type)

        if type_info.base_type == bool:
            return False

        if type_info.base_type == str:
            return ""

        if type_info.is_mapping:
            return {}

        if type_info.is_many:
            return []

        return None
