from django.urls import path
from .views import game_view
from .views import update_leaderboard

urlpatterns = [
    path("bingame/", game_view, name="bingame"),
    path('update-leaderboard/', update_leaderboard, name='update-leaderboard'),
]
