from django.contrib import admin
from .models import GardenState
# Register your models here.
class GardenStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    search_fields = ('user', 'updated_at')
    
admin.site.register(GardenState, GardenStateAdmin)