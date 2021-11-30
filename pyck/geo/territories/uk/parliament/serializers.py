import dataclasses

from rest_framework.serializers import Field
from rest_framework_dataclasses.serializers import DataclassSerializer


class EmbeddedValueField(Field):
    def __init__(self, serializer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer = serializer

    def to_internal_value(self, data):
        return self.serializer.to_internal_value(data["value"])

    def to_representation(self, value):
        return {"value": self.serializer.to_representation(value)}


def embedded_value(dataclass):
    dataclass_serializer = type(
        f"{dataclass.__name__}Serializer",
        (DataclassSerializer,),
        {"Meta": type("Meta", (), {"dataclass": dataclass})},
    )
    return dataclasses.field(
        metadata={"serializer_field": EmbeddedValueField(dataclass_serializer())}
    )
