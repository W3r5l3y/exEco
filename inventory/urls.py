from django.urls import path
from .views import inventory_view, open_lootbox, get_inventory
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('inventory/', inventory_view, name='inventory'),
    path('open-lootbox/<int:lootbox_id>/', open_lootbox, name='open_lootbox'),
    path('get-inventory/', get_inventory, name='get_inventory'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
