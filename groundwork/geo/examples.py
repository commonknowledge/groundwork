from typing import Any, List

from django.urls import path
from django.views.generic import TemplateView


class MapExampleView(TemplateView):
    template_name = "groundwork/geo/examples/map_example.html"

    @property
    def sources(self):
        return {
            "mapbox-terrain": {
                "type": "vector",
                "url": "mapbox://mapbox.mapbox-terrain-v2",
            }
        }

    @property
    def layers(self):
        return [
            {
                "id": "terrain-data",
                "type": "line",
                "source": "mapbox-terrain",
                "source-layer": "contour",
                "layout": {"line-join": "round", "line-cap": "round"},
                "paint": {"line-color": "#ff69b4", "line-width": 1},
            }
        ]


urlpatterns: List[Any] = [path("map/", MapExampleView.as_view())]
