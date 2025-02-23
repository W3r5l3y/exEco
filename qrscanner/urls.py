from django.urls import path
from .views import scan_qr, get_qrscanner_leaderboard

urlpatterns = [
    path("qrscanner/", scan_qr, name="scan_qr"),
    path("get-qrscanner-leaderboard/", get_qrscanner_leaderboard, name="get_qrscanner_leaderboard"),
]
