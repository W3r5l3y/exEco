from django.urls import path
from .views import (
    transport_view,
    strava_login,
    strava_callback,
    get_latest_activity,
    get_last_five_activities,
    log_activity,
    get_transport_leaderboard,
    get_transport_stats,
    transport_error,
)

urlpatterns = [
    path("transport/", transport_view, name="transport"),
    path("transport-error/", transport_error, name="transport-error"),
    path("strava-login/", strava_login, name="strava-login"),
    path("strava-callback/", strava_callback, name="strava-callback"),
    path("get-latest-activity/", get_latest_activity, name="get-latest-activity"),
    path(
        "get-last-five-activities/",
        get_last_five_activities,
        name="get_last_five_activities",
    ),
    path("log-activity/", log_activity, name="log_activity"),
    path("get-transport-stats/", get_transport_stats, name="get_transport_stats"),
    path(
        "get-transport-leaderboard/",
        get_transport_leaderboard,
        name="get_transport_leaderboard",
    ),
]
