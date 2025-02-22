from django.urls import path
from .views import game_view, get_leaderboard, update_leaderboard, fetch_random_items


urlpatterns = [
    path("bingame/", game_view, name="bingame"),
    path('update-leaderboard/', update_leaderboard, name='update-leaderboard'),
    path("get-leaderboard/", get_leaderboard, name="get_leaderboard"),
    path('fetch_random_items/', fetch_random_items, name='fetch_random_items'),
]
