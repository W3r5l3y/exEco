from django.contrib import admin

# Register your models here.
from .models import StravaToken, LoggedActivity

class StravaTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_token', 'refresh_token', 'expires_at', 'athlete_id')
    search_fields = ('user__email', 'athlete_id')

class LoggedActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_id', 'distance', 'activity_type', 'created_at')
    search_fields = ('user__email', 'activity_id')
    list_editable = ('activity_type', 'distance')

admin.site.register(StravaToken, StravaTokenAdmin)
admin.site.register(LoggedActivity, LoggedActivityAdmin)