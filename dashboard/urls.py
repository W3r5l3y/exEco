from django.urls import path
from .views import dashboard_view, get_total_leaderboard

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("get-total-leaderboard/", get_total_leaderboard, name="get_total_leaderboard"),
]
