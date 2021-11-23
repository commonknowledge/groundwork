from typing import Any, Dict, Optional

import re
from itertools import zip_longest

from django import template
from django.conf import settings
from django.template.base import token_kwargs
from django.template.library import Library, parse_bits
from django.template.loader import get_template

from pyck.core.template import register_block_tag

register = Library()


MAP_TEMPLATE = get_template("pyck/geo/components/map.html")


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
    """
    Renders a mapbox map widget.

    Usage:

    ```
    {% load ckgeo_tags %}

    {% map class="vw-100 vh-100" center="[4.53,52.22]" zoom=9 %}
        {% comment %} map configuration tags go here {% endcomment %}
    {% endmap %}
    ```

    Args:
        element: Return a cache key given the arguments to the function
        style: Override the map style on a per-map basis. Defaults to the MAPBOX_DEFAULT_STYLE django config.
        api_key: Override the map api key on a per-map basis. Defaults to the MAPBOX_PUBLIC_API_KEY django config.
        center: Initial [lon,lat] location to center the map on.
        zoom: Initial zoom value. Defaults to 9.
        **attrs: Any additional kwargs are used as html attributes on the map.

    Returns:
        Rendered html for a map widget.

    # noqa: DAR101 context
    # noqa: DAR101 children
    """
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
