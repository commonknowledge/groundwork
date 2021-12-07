from typing import Any, List

from django.urls import include, path

from example.uk import views

urlpatterns: List[Any] = [path("mps/", views.MpListView.as_view())]
