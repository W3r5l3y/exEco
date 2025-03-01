from django.apps import AppConfig
from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.dispatch import receiver

import sys

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        post_migrate.connect(load_fixtures_after_migrate, sender=self)
            
            

def load_fixtures_after_migrate(sender, **kwargs):
    #Load fixtures after database has been made (gives location for items to go into)
    if sender.name == 'inventory':
        if 'test' in sys.argv:
            return
        #import here so it runs after models made
        from inventory.models import LootboxTemplate
        # Optional: Only load fixtures if there's nothing in the table yet (avoids duplicates).
        if not LootboxTemplate.objects.exists():
            try:
                call_command('loaddata', 'lootbox_templates.json')
                call_command('loaddata', 'lootbox_contents.json')
                print("Lootbox templates and contents loaded automatically via post_migrate.")
            except Exception as e:
                print(f"Error loading fixtures in post_migrate: {e}")