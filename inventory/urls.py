from django.urls import path
from .views import inventory_view, open_lootbox, get_inventory, get_corresponding_lootbox_template, merge_item 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('inventory/', inventory_view, name='inventory'),
    path('open-lootbox/<int:lootbox_id>/', open_lootbox, name='open_lootbox'),
    path('get-inventory/', get_inventory, name='get_inventory'),
    path('get-corresponding-lootbox-template/<int:item_id>/', get_corresponding_lootbox_template, name='get_corresponding_lootbox_template'),
    path('merge-item/<int:item_id>/', merge_item, name='merge_item'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
