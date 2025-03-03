from django.db import models
#from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Inventory Table - Links each user to their inventory
class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def addItem(self, name, image=None, item_type="regular", quantity=1):
        #Add an item to the user inventory, if it already exists add 1 to quantity
        if quantity < 1:
            return False  # Prevent adding zero or negative quantities

        item, created = InventoryItem.objects.get_or_create(
            inventory=self,
            name=name,
            defaults={"image": image, "item_type": item_type, "quantity": quantity}
        )
        
        if not created:
            item.quantity += quantity
            item.save()

        return item

    def addLootbox(self, lootbox_template, quantity=1):
        #Add lootbox to a user inventory, if it exists already add 1 to quantity 
        if quantity < 1:
            return False  # Prevent invalid quantity

        lootbox, created = InventoryItem.objects.get_or_create(
            inventory=self,
            name=lootbox_template.name,  # Assuming lootbox template has a name
            defaults={"image": lootbox_template.lootbox_image, "item_type": "lootbox", "quantity": quantity, "lootbox_template": lootbox_template}
        )
        if not created:
            lootbox.quantity += quantity
            lootbox.save()
        return lootbox

    def __str__(self):
        return f"{self.user.email}'s Inventory"

# Item Type - Regular Item or Lootbox
class ItemType(models.TextChoices):
    REGULAR = "regular", "Regular Item"
    LOOTBOX = "lootbox", "Lootbox"

# Lootbox Template - Defines a lootbox type with fixed rewards
class LootboxTemplate(models.Model):
    lootbox_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    lootbox_image = models.ImageField(upload_to="static/img/lootboxes/")
    
    def __str__(self):
        return self.name

# Lootbox Item - Defines items that appear inside lootboxes (not in inventory)
class LootboxItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="static/img/items/")

    def __str__(self):
        return self.name

# Lootbox Contents - Stores what items are inside each lootbox (not in inventory)
class LootboxContents(models.Model):
    lootbox_template = models.ForeignKey(LootboxTemplate, on_delete=models.CASCADE, related_name="contents")
    item = models.ForeignKey(LootboxItem, on_delete=models.CASCADE)
    probability = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])  # Probability (0 to 1)

    def __str__(self):
        return f"{self.item.name} in {self.lootbox_template.name} ({self.probability * 100}%)"

# Inventory Item - Stores only ACTUAL owned items (not lootbox contents)
class InventoryItem(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    item_type = models.CharField(max_length=10, choices=ItemType.choices, default=ItemType.REGULAR)
    image = models.ImageField(upload_to="static/img/items/")
    quantity = models.PositiveIntegerField(default=1)

    # If it's a lootbox, link it to a LootboxTemplate
    lootbox_template = models.ForeignKey(LootboxTemplate, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically delete empty items (instead of marking inactive)
        if self.quantity == 0:
            self.delete()
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (x{self.quantity}) - {self.inventory.user.email}"
