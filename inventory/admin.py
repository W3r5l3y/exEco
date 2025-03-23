from django.contrib import admin
from .models import (
    Inventory,
    InventoryItem,
    LootboxTemplate,
    LootboxItem,
    LootboxContents,
)


# Register your models here.
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("inventory_id", "user")
    search_fields = ("inventory_id", "user")


class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("inventory", "name", "item_type", "quantity", "lootbox_template")
    search_fields = ("inventory", "name")
    list_editable = ("name", "item_type", "quantity")


class LootboxTemplateAdmin(admin.ModelAdmin):
    list_display = ("lootbox_id", "name", "lootbox_image")
    search_fields = ("lootbox_id", "name")
    list_editable = ("name", "lootbox_image")


class LootboxItemAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "image")
    search_fields = ("name", "description")
    list_editable = ("description", "image")


class LootboxContentsAdmin(admin.ModelAdmin):
    list_display = ("lootbox_template", "item", "probability")
    search_fields = ("lootbox_template", "item")
    list_editable = ("item", "probability")


admin.site.register(Inventory, InventoryAdmin)
admin.site.register(InventoryItem, InventoryItemAdmin)
admin.site.register(LootboxTemplate, LootboxTemplateAdmin)
admin.site.register(LootboxItem, LootboxItemAdmin)
admin.site.register(LootboxContents, LootboxContentsAdmin)
