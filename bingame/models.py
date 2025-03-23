from django.db import models
from accounts.models import CustomUser


# The table for bins
class Bins(models.Model):
    bin_id = models.AutoField(primary_key=True)
    bin_name = models.CharField(max_length=100)
    bin_image = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.bin_name} with image held as {self.bin_image}"


# The table for items
class Items(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=100)
    item_image = models.ImageField(upload_to="bingame/items/", blank=True, null=True)
    bin_id = models.ForeignKey(Bins, on_delete=models.CASCADE)

    @classmethod
    def add_item(cls, item_name, bin_id, item_image=None):
        # Check if the item already exists
        if cls.objects.filter(item_name=item_name).exists():
            return False

        if not item_image:
            item_image = f"Bingame/Items/{item_name.replace(' ', '_').lower()}.png"

        # Add a bingame item to the bingame database - assumes that the items img url is item_name.png

        # Create the item
        item = cls.objects.create(
            item_name=item_name, item_image=item_image, bin_id=bin_id
        )
        return True

    def __str__(self):
        return f"{self.item_name}, with image held as {self.item_image}"
