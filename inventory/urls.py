from django.urls import path
from .views import inventory_view, open_lootbox, get_inventory


urlpatterns = [
    path('inventory/', inventory_view, name='inventory'),
    path('open-lootbox/<int:lootbox_id>/', open_lootbox, name='open_lootbox'),
    path('get-inventory/', get_inventory, name='get_inventory'),
]
