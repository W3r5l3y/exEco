from django.urls import path
from .views import transport_view, strava_login, strava_callback, get_latest_activity

urlpatterns = [
    path("transport/", transport_view, name="transport"),
    path('strava-login/', strava_login, name='strava-login'),
    path('strava-callback/', strava_callback, name='strava-callback'),
    path("get-latest-activity/", get_latest_activity, name="get-latest-activity"),
]
