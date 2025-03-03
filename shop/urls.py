from django.urls import path
from .views import shop_view, buy_item
#from .views import null

urlpatterns = [
    path('shop/', shop_view, name='shop'),
    path('buy-item/<int:item_id>/', buy_item, name='buy_item'),
]