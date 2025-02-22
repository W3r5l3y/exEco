from django.urls import path
from .views import transport_view, strava_login, strava_callback, get_latest_activity, get_last_five_activities, log_activity, get_stats, get_transport_leaderboard

urlpatterns = [
    path("transport/", transport_view, name="transport"),
    path('strava-login/', strava_login, name='strava-login'),
    path('strava-callback/', strava_callback, name='strava-callback'),
    path("get-latest-activity/", get_latest_activity, name="get-latest-activity"),
    path("get-last-five-activities/", get_last_five_activities, name="get_last_five_activities"),
    path("log-activity/", log_activity, name="log_activity"),
    path("get-stats/", get_stats, name="get_stats"),
    path("get-transport-leaderboard/", get_transport_leaderboard, name="get_transport_leaderboard"),
]
