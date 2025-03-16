from django.urls import path
from .views import garden_view, save_garden, load_garden, load_inventory, save_garden_as_image, fetch_user_garden_image, get_tree_image
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("garden/", garden_view, name="garden"),
    path("save-garden/", save_garden, name="save_garden"),
    path("load-garden/", load_garden, name="load_garden"),
    path("load-inventory/", load_inventory, name="load_inventory"),
    path("save-garden-as-image/", save_garden_as_image, name="save_garden_as_image"),
    path("fetch-user-garden-image/", fetch_user_garden_image, name="fetch_user_garden_image"),
    path("get-tree-image/", get_tree_image, name="get_tree_image"), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)