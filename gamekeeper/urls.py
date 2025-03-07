from django.urls import path
from .views import gamekeeper_view


urlpatterns = [
    path('gamekeeper/', gamekeeper_view, name='gamekeeper'),
]
