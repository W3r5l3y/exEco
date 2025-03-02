from django.urls import path
from .views import qrscanner, get_qrscanner_leaderboard

urlpatterns = [
    path("qrscanner/", qrscanner, name="qrscanner"),
    path(
        "get-qrscanner-leaderboard/",
        get_qrscanner_leaderboard,
        name="get_qrscanner_leaderboard",
    ),
]
