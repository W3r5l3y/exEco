from django.urls import path
from .views import (game_view, update_leaderboard, fetch_random_items, get_bingame_leaderboard, get_lootbox_data,)


urlpatterns = [
    path("bingame/", game_view, name="bingame"),
    path("update-leaderboard/", update_leaderboard, name="update_leaderboard"),
    path("get-bingame-leaderboard/", get_bingame_leaderboard, name="get_bingame_leaderboard"),
    path("fetch-random-items/", fetch_random_items, name="fetch_random_items"),
    path("get-lootbox-data/", get_lootbox_data, name="get_lootbox_data"),
]
