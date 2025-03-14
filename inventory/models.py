from django.db import models
#from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Inventory Table - Links each user to their inventory
class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def addItem(self, name, image=None, item_type="regular", description=None, quantity=1, stats=None):
        print(f"Adding item to inventory: {name}, {quantity}")
        #Add an item to the user inventory, if it already exists add 1 to quantity
        if quantity < 1:
            return False  # Prevent adding zero or negative quantities

        item, created = InventoryItem.objects.get_or_create(
            inventory=self,
            name=name,
            defaults={
                "image": image,
                "item_type": item_type,
                "description": description,
                "quantity": quantity,
                "aesthetic_appeal": stats.get("aesthetic_appeal", 0),
                "habitat": stats.get("habitat", 0),
                "carbon_uptake": stats.get("carbon_uptake", 0),
                "waste_reduction": stats.get("waste_reduction", 0),
                "health_of_garden": stats.get("health_of_garden", 0),
                "innovation": stats.get("innovation", 0), 
            }
        )
        
        if not created:
            item.quantity += quantity
            item.save()
        #print(f"Item added to inventory: {item.name}, {item.quantity}") #DEBUG
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
    lootbox_image = models.ImageField(upload_to="inventory/lootboxes/", blank=True, null=True) 
    
    def __str__(self):
        return self.name

# Lootbox Item - Defines items that appear inside lootboxes (not in inventory)
class LootboxItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="inventory/items/", blank=True, null=True) 
    aesthetic_appeal = models.IntegerField(default=2)
    habitat = models.IntegerField(default=2)
    carbon_uptake = models.IntegerField(default=0)
    waste_reduction = models.IntegerField(default=0)
    health_of_garden = models.IntegerField(default=0)
    innovation = models.IntegerField(default=0)

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
    item_type = models.CharField(max_length=10, choices=ItemType.choices, default=ItemType.REGULAR)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="inventory/items/", blank=True, null=True) 
    quantity = models.PositiveIntegerField(default=1)
    # Stats
    aesthetic_appeal = models.IntegerField(default=0) 
    habitat = models.IntegerField(default=0)
    carbon_uptake = models.IntegerField(default=0)
    waste_reduction = models.IntegerField(default=0)
    health_of_garden = models.IntegerField(default=0)
    innovation = models.IntegerField(default=0)
    # If it's a lootbox, link it to a LootboxTemplate
    lootbox_template = models.ForeignKey(LootboxTemplate, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.quantity == 0:
            self.delete()
        else:
            super().save(*args, **kwargs)

    @property
    def is_mergeable(self):
        """
        Returns True if this is a regular item and it can only be obtained from a lootbox,
        as indicated by its presence in LootboxContents.
        """
        if self.item_type != "regular":
            return False
        # If the item is present in any LootboxContents, we assume it is mergeable.
        return LootboxContents.objects.filter(item__name=self.name).exists()

    def __str__(self):
        return f"{self.name} (x{self.quantity}) - {self.inventory.user.email}"