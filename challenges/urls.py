from django.urls import path
from .views import challenges_view, get_reset_times

urlpatterns = [
    path("challenges/", challenges_view, name="challenges"),
    path("get-reset-times/", get_reset_times, name="get_reset_times"),
]
