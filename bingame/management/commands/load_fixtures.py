from django.core.management.base import BaseCommand
import subprocess

class Command(BaseCommand):
    help = "Load fixtures for bingame, shop, and inventory"

    def handle(self, *args, **kwargs):
        self.stdout.write("Applying migrations...")
        subprocess.run(["python", "manage.py", "migrate"], check=True)

        fixtures = [
            "inventory/fixtures/lootbox_templates_fixture.json",
            "bingame/fixtures/bingame_fixture.json",
            "shop/fixtures/shop_fixture.json",
            "inventory/fixtures/lootbox_contents_fixture.json",
        ]

        for fixture in fixtures:
            self.stdout.write(f"Loading {fixture}...")
            subprocess.run(["python", "manage.py", "loaddata", fixture], check=True)

        self.stdout.write(self.style.SUCCESS("Fixtures loaded successfully!"))
