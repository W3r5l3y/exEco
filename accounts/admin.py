from django.contrib import admin
from .models import UserPoints


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ("user", "bingame_points", "qrscanner_points", "transport_points", "total_points")
    search_fields = ("user__email",)
    list_editable = ("bingame_points", "qrscanner_points", "transport_points",)
