from typing import Any, List

from django.urls import path

from example.geo import views

urlpatterns: List[Any] = [path("map/", views.MapExampleView.as_view())]
