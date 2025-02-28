from django.db import models
from django.contrib.auth.models import User
#Create your models here
class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Inventory"

class ItemType(models.TextChoices):
    REGULAR = "regular", "Regular Item"
    LOOTBOX = "lootbox", "Lootbox"

class Item(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=100)
    item_description = models.TextField(blank=True, null=True)
    item_type = models.CharField(max_length=10, choices=ItemType.choices, default=ItemType.REGULAR)
    item_image = models.ImageField(upload_to="static/img/items/")
    item_quantity = models.PositiveIntegerField(default=1)

    # If quantity goes below 0, delete the item - helps with views.py hopefully can just do quantity - 1, in case of there being stacks of items
    def save(self, *args, **kwargs):
        if self.item_quantity == 0:
            self.delete()
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} (x{self.item_quantity}) - {self.inventory.user.username}"

class LootboxContent(models.Model):
    lootbox = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="lootbox_contents", limit_choices_to={'item_type': ItemType.LOOTBOX})
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="contained_in_lootboxes")
    probability = models.FloatField(help_text="Probability of getting this item from the lootbox (0-1)")

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(probability__gte=0, probability__lte=1), name="valid_probability_range")
        ]

    def __str__(self):
        return f"{self.item.item_name} in {self.lootbox.item_name} ({self.probability * 100}%)"
