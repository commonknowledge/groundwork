from typing import Any, List

from django.urls import path
from django.views.generic import TemplateView

from example.geo import views

urlpatterns: List[Any] = [
    path("map/", views.MapExampleView.as_view()),
    path(
        "map/marker/", TemplateView.as_view(template_name="geo/map_marker_example.html")
    ),
]
