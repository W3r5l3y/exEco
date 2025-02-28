from django.test import TestCase
from .models import Inventory, InventoryItem, ItemType, LootboxTemplate, LootboxItem, LootboxContents
from accounts.models import CustomUser

"""
MODELS TESTING
"""

class InventoryModelTests(TestCase):

    def setUp(self):
        #Crreate a user 
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", 
            first_name="Test", 
            last_name="User", 
            password="password123"
        )
        self.inventory = Inventory.objects.create(user=self.user)

    def test_inventory_creation(self):
        #Check inventory creation for user
        self.assertEqual(self.inventory.user.email, "testuser@example.com")
    
    def test_add_inventory_item(self):
        #Check adding an item to the inventory works correctly
        item = InventoryItem.objects.create(
            inventory=self.inventory,
            name="Snake Plant",
            item_type=ItemType.REGULAR,
            quantity=1
        )
        self.assertEqual(item.name, "Snake Plant")
        self.assertEqual(item.item_type, ItemType.REGULAR)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(self.inventory.items.count(), 1)

    def test_add_multiple_items(self):
        #Check adding multiple items to inventory works correctly
        plant1 = InventoryItem.objects.create(
            inventory=self.inventory,
            name="Moonflower",
            item_type=ItemType.REGULAR,
            quantity=2
        )
        plant2 = InventoryItem.objects.create(
            inventory=self.inventory,
            name="Sunflower",
            item_type=ItemType.REGULAR,
            quantity=3
        )
        self.assertEqual(self.inventory.items.count(), 2)
        self.assertEqual(plant1.name, "Moonflower")
        self.assertEqual(plant2.name, "Sunflower")
        self.assertEqual(plant1.quantity, 2)
        self.assertEqual(plant2.quantity, 3)

    def test_item_deletion_on_zero_quantity(self):
        #Check item is deleted when quantity is zero
        item = InventoryItem.objects.create(
            inventory=self.inventory,
            name="Wilted Leaf",
            item_type=ItemType.REGULAR,
            quantity=1
        )
        item.quantity = 0
        item.save()
        self.assertEqual(InventoryItem.objects.filter(name="Wilted Leaf").count(), 0)
        
class LootboxModelTests(TestCase):

    def setUp(self):
        #Setup test user for checking lootbox models
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", 
            first_name="Test", 
            last_name="User", 
            password="password123"
        )
        self.inventory = Inventory.objects.create(user=self.user)

        #Create lootbox template
        self.lootbox_template = LootboxTemplate.objects.create(name="Bingame Lootbox")

        # Create possible lootbox items 
        self.rare_bin = LootboxItem.objects.create(name="Gold-bin", description="Sick gold bin")
        self.common_bin = LootboxItem.objects.create(name="Grey-bin", description="Rubbish petty grey bin")

        # Add plant items to the lootbox with probabilities
        LootboxContents.objects.create(lootbox_template=self.lootbox_template, item=self.rare_bin, probability=0.1)
        LootboxContents.objects.create(lootbox_template=self.lootbox_template, item=self.common_bin, probability=0.9)

    def test_lootbox_creation(self):
        #Check if lootbox is created correctly
        self.assertEqual(self.lootbox_template.name, "Bingame Lootbox")

    def test_lootbox_contents(self):
        #Check if lootbox contains the items added to its tempalte
        contents = LootboxContents.objects.filter(lootbox_template=self.lootbox_template)
        self.assertEqual(contents.count(), 2)
        item_names = [content.item.name for content in contents]
        self.assertIn("Gold-bin", item_names)
        self.assertIn("Grey-bin", item_names)

    def test_adding_lootbox_to_inventory(self):
        #Check adding a lootbox to a users inventory works correctly
        lootbox_item = InventoryItem.objects.create(
            inventory=self.inventory,
            name="Bingame Lootbox",
            item_type=ItemType.LOOTBOX,
            lootbox_template=self.lootbox_template,
            quantity=1
        )
        self.assertEqual(lootbox_item.name, "Bingame Lootbox")
        self.assertEqual(lootbox_item.item_type, ItemType.LOOTBOX)
        self.assertEqual(lootbox_item.lootbox_template.name, "Bingame Lootbox")
        self.assertEqual(self.inventory.items.count(), 1)

"""
TESTING VIEWS
"""