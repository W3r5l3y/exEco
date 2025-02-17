from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "location_code",
        "location_name",
        "cooldown_length",
        "times_visited",
    )
    search_fields = ("location_code", "location_name")
    list_filter = ("cooldown_length",)
