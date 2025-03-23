from django.urls import path
from .views import shop_view, buy_item
from django.conf import settings
from django.conf.urls.static import static

# from .views import null

urlpatterns = [
    path("shop/", shop_view, name="shop"),
    path("buy-item/<int:item_id>/", buy_item, name="buy_item"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
