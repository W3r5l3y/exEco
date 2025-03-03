from django.contrib import admin
from .models import Bins, Items


# Register your models here.
class BinsAdmin(admin.ModelAdmin):
    list_display = ("bin_id", "bin_name", "bin_image")
    search_fields = ("bin_id", "bin_name")
    list_editable = ("bin_name", "bin_image")


class ItemsAdmin(admin.ModelAdmin):
    list_display = ("item_id", "item_name", "item_image", "bin_id")
    search_fields = ("item_id", "item_name", "bin_id")
    list_editable = ("item_name", "item_image", "bin_id")

admin.site.register(Bins, BinsAdmin)
admin.site.register(Items, ItemsAdmin)
