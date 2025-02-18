from django.urls import path
from .views import transport_view

urlpatterns = [
    path("transport/", transport_view, name="transport"),
]
