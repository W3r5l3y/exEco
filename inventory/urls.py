from django.urls import path
from .views import inventory_view, open_lootbox


urlpatterns = [
    path('inventory/', inventory_view, name='inventory'),
    path('open-lootbox/<int:lootbox_id>/', open_lootbox, name='open_lootbox'),
]
