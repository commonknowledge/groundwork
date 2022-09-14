from typing import Any

from django.template import Context, Template
from django.test import TestCase, override_settings


@override_settings(MAPBOX_PUBLIC_API_KEY="dummy")
class GeoTagsTestCase(TestCase):
    def test_renders_map(self):
        html = render_template(
            "{% load groundwork_geo %}" '{% map class="w-100" zoom=9 %}' "{% endmap %}"
        )

        self.assertInHTML(
            '<div class="w-100" data-controller="map" data-map-zoom-value="9" data-map-api-key-value="dummy">'
            '<div data-map-target="canvas"></div>'
            "</div>",
            html,
        )

    def test_renders_map_in_place_false_without_canvas(self):
        html = render_template(
            "{% load groundwork_geo %}"
            '{% map in_place=False class="w-100" zoom=9 %}'
            "{% endmap %}"
        )

        self.assertInHTML(
            '<div class="w-100" data-controller="map" data-map-zoom-value="9" data-map-api-key-value="dummy">'
            "</div>",
            html,
        )

    def test_renders_map_in_place_false_with_canvas(self):
        html = render_template(
            "{% load groundwork_geo %}"
            '{% map in_place=False class="w-100" zoom=9 %}'
            '{% map_canvas class="w-50" %}'
            "{% endmap %}"
        )

        self.assertInHTML(
            '<div class="w-100" data-controller="map" data-map-zoom-value="9" data-map-api-key-value="dummy">'
            '<div class="w-50" data-map-target="canvas"></div>'
            "</div>",
            html,
        )


def render_template(content: str) -> Any:
    context = Context()
    template_to_render = Template(content)

    return template_to_render.render(context)
