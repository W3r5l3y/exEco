from django.urls import path
from .views import (
    game_view,
    update_leaderboard,
    fetch_random_items,
    get_bingame_leaderboard,
)


urlpatterns = [
    path("bingame/", game_view, name="bingame"),
    path("update-leaderboard/", update_leaderboard, name="update-leaderboard"),
    path(
        "get-bingame-leaderboard/",
        get_bingame_leaderboard,
        name="get_bingame_leaderboard",
    ),
    path("fetch_random_items/", fetch_random_items, name="fetch_random_items"),
]
