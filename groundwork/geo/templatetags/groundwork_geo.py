from typing import Any, Dict, List, Optional, Union

import json

from django import template
from django.conf import settings
from django.template.base import token_kwargs
from django.template.library import Library, parse_bits
from django.template.loader import get_template

from groundwork.core.template import register_block_tag

register = Library()

JsonLiteralOrObject = Union[str, Dict, List]


MAP_TEMPLATE = get_template("groundwork/geo/components/map.html")
MAP_CONFIG_TEMPLATE = get_template("groundwork/geo/components/map_config.html")


@register_block_tag(library=register, takes_context=True)
def map(
    context: Any,
    element: str = "div",
    style: Optional[str] = None,
    api_key: Optional[str] = None,
    center: Any = None,
    zoom: Optional[int] = None,
    children: Optional[template.NodeList] = None,
    **attrs: Dict[str, str],
) -> template.Node:
    if api_key is None:
        api_key = getattr(settings, "MAPBOX_PUBLIC_API_KEY", None)

    if style is None:
        style = getattr(settings, "MAPBOX_DEFAULT_STYLE", None)

    return MAP_TEMPLATE.render(
        {
            "element": element,
            "values": (
                ("api-key", api_key),
                ("center", _to_json_str(center)),
                ("style", _to_json_str(style)),
                ("zoom", _to_json_str(zoom)),
            ),
            "attrs": tuple(attrs.items()),
            "slots": children.render(context) if children else "",
        }
    )


@register_block_tag(library=register, takes_context=True, upto="endmarker")
def map_marker(
    context: Any,
    location: JsonLiteralOrObject,
    children: Optional[template.NodeList] = None,
):
    return MAP_CONFIG_TEMPLATE.render(
        {
            "controller": "map-marker",
            "values": {"location": _to_json_str(location)},
            "children": children.render(context) if children else "",
        }
    )


@register.inclusion_tag("groundwork/geo/components/map_config.html")
def map_source(id, data):
    ref = "map_source_config"

    return {
        "controller": "map-source",
        "values": {"id": id, "data": "#" + ref},
        "json": {ref: data},
    }


@register.inclusion_tag("groundwork/geo/components/map_config.html")
def map_layer(layer):
    ref = "map_layer_config"

    return {
        "controller": "map-layer",
        "values": {"layer": "#" + ref},
        "json": {ref: layer},
    }


def _to_json_str(val: JsonLiteralOrObject) -> Optional[str]:
    if val is None or isinstance(val, (str, float, int)):
        return val

    if hasattr(val, "json"):
        return _to_json_str(val.json)

    return json.dumps(val)
