from django.urls import path
from .views import garden_view, save_garden, load_garden

urlpatterns = [
    path("garden/", garden_view, name="garden"),
    path("save-garden/", save_garden, name="save_garden"),
    path("load-garden/", load_garden, name="load_garden"),
]
