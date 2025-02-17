from django.urls import path
from .views import scan_qr

urlpatterns = [
    path("qrscanner/", scan_qr, name="scan_qr"),
]
