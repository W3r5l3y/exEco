from django.urls import path
from .views import login_register_view

urlpatterns = [
    path("login/", login_register_view, name="login"),
]
