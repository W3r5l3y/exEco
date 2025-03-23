from django.urls import path
from .views import challenges_view, submit_challenge, get_reset_times

urlpatterns = [
    path("challenges/", challenges_view, name="challenges"),
    path("submit-challenge/", submit_challenge, name="submit_challenge"),
    path("get-reset-times/", get_reset_times, name="get_reset_times"),
]
