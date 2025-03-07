from django.urls import path
from .views import gamekeeper_view, add_location_to_qr


urlpatterns = [
    path('gamekeeper/', gamekeeper_view, name='gamekeeper'),
    path('add-location-to-qr/<str:location_code>/<str:location_name>/<str:location_fact>/<int:cooldown_length>/<int:location_value>/', add_location_to_qr, name='add_location_to_qr')
]
