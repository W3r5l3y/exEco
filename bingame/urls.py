from django.urls import path
from .views import game_view

urlpatterns = [
    path("bingame/", game_view, name="bingame"),
]
