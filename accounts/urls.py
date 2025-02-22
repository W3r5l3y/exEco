from django.urls import path
from .views import login_register_view, settings_view

urlpatterns = [
    path("login/", login_register_view, name="login"),
    path("settings/", settings_view, name="settings"),
]
