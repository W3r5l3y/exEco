from django.contrib import admin
from .models import Location


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "location_code",
        "location_name",
        "location_value",
        "cooldown_length",
        "times_visited",
    )
    search_fields = ("location_code", "location_name")
    list_editable = (
        "location_name",
        "location_value",
        "cooldown_length",
        "times_visited",
    )


admin.site.register(Location, LocationAdmin)
