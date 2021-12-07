from typing import Any, List

from django.urls import include, path

urlpatterns: List[Any] = [
    path("geo/", include("pyck.geo.examples")),
    path("uk/", include("example.uk.urls")),
]
