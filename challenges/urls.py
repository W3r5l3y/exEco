from django.urls import path
from .views import challenges_view, submit_challenge

urlpatterns = [
    path("challenges/", challenges_view, name="challenges"),
    path("submit-challenge/", submit_challenge, name="submit_challenge"),
]
