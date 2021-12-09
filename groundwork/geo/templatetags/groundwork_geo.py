from typing import Any, Dict, Optional

import functools

from django import template
from django.conf import settings
from django.template.base import token_kwargs
from django.template.library import Library, parse_bits
from django.template.loader import get_template

from groundwork.core.template import register_block_tag

register = Library()


MAP_TEMPLATE = get_template("groundwork/geo/components/map.html")


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
                ("center", center),
                ("style", style),
                ("zoom", zoom),
            ),
            "attrs": tuple(attrs.items()),
            "slots": children.render(context) if children else "",
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
