from typing import Any, List

from django.urls import include, path

urlpatterns: List[Any] = [
    path("geo/", include("groundwork.geo.examples")),
    path("uk/", include("example.uk.urls")),
]
