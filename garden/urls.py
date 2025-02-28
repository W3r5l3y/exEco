from django.urls import path
from .views import (
    garden_view,
)

urlpatterns = [
    path("garden/", garden_view, name="garden"),
]
