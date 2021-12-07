from typing import Any, Type

import dataclasses

from rest_framework.serializers import Field
from rest_framework_dataclasses.serializers import DataclassSerializer


class EmbeddedValueField(Field):
    """
    Serializer field for decoding embeded resources of the form

    ```
    {"value": {...the thing we actually want }, "links": [...]}
    ```

    Wraps an inner serializer, extracts the value field from the returned data and returns that.
    """

    def __init__(self, serializer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer = serializer

    def to_internal_value(self, data):
        return self.serializer.to_internal_value(data["value"])

    def to_representation(self, value):
        return {"value": self.serializer.to_representation(value)}


def embedded_value(dataclass: Type[Any]) -> dataclasses.Field:
    """
    Convenience function for returning a dataclass field descriptor that informs `DataclassSerializer` that we wish
    to use the EmbeddedValueField serializer.

    Args:
        dataclass: A dataclass type to deserialize the embedded value to

    Returns:
        A dataclass field descriptor.
    """

    dataclass_serializer = type(
        f"{dataclass.__name__}Serializer",
        (DataclassSerializer,),
        {"Meta": type("Meta", (), {"dataclass": dataclass})},
    )
    return dataclasses.field(
        metadata={"serializer_field": EmbeddedValueField(dataclass_serializer())}
    )
