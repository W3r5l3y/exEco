from django.urls import path
from .views import qrcode_view

urlpatterns = [
    path("qrscanner/", qrcode_view, name="qrscanner"),
]
