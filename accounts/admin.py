from django.contrib import admin
from .models import UserPoints


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ("user", "points_scored")
    search_fields = ("user__email",)
    list_editable = ("points_scored",)
