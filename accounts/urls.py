from django.urls import path
from .views import (
    login_register_view,
    settings_view,
    logout_view,
    tos_view,
    privacy_view,
)

urlpatterns = [
    path("login/", login_register_view, name="login"),
    path("settings/", settings_view, name="settings"),
    path("logout/", logout_view, name="logout"),
    path("tos/", tos_view, name="tos"),
    path("privacy/", privacy_view, name="privacy"),
]
