from django.contrib import admin
from .models import ShopItems


# Register your models here.
class ShopItemsAdmin(admin.ModelAdmin):
    list_display = ("itemId", "name", "description", "image", "cost")
    search_fields = ("itemId", "name", "description", "cost")
    list_editable = ("name", "description", "image", "cost")



admin.site.register(ShopItems, ShopItemsAdmin)
