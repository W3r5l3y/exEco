from django.urls import path
from .views import transport_view, strava_login, strava_callback

urlpatterns = [
    path("transport/", transport_view, name="transport"),
    path('strava-login/', strava_login, name='strava-login'),
    path('strava-callback/', strava_callback, name='strava-callback'),
]
