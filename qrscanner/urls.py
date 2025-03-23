from django.urls import path
from .views import qrscanner, get_qrscanner_leaderboard, locations_json

urlpatterns = [
    path("qrscanner/", qrscanner, name="qrscanner"),
    path("get-qrscanner-leaderboard/", get_qrscanner_leaderboard, name="get_qrscanner_leaderboard"),
    path("locations-json/", locations_json, name="locations_json"),
]
