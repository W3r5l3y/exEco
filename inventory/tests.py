from django.test import TestCase, Client
from .models import Inventory, InventoryItem, ItemType, LootboxTemplate, LootboxItem, LootboxContents
from accounts.models import CustomUser
from django.urls import reverse
import random

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

    def test_add_item_new(self):
        #Test using '.addItem()' method to add a new item to inventory
        item = self.inventory.addItem(name="Rainflower", quantity=2)

        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Rainflower")
        self.assertEqual(item.quantity, 2)
        
        # Check item is in correct inventory
        self.assertEqual(item.inventory, self.inventory)
        self.assertEqual(self.inventory.items.count(), 1)

    def test_add_item_existing(self):
        #Test using '.addItem()' method to add an item that already exists in inventory
        self.inventory.addItem(name="Mistflower", quantity=2)
        item = self.inventory.addItem(name="Mistflower", quantity=3)  # Add more
        
        self.assertEqual(item.quantity, 5)  # ✅ Quantity should be updated
        self.assertEqual(item.inventory, self.inventory)
        self.assertEqual(self.inventory.items.count(), 1)  # Still only one item

    def test_add_lootbox(self):
        #Test adding a lootbox to the inventory
        lootbox_template = LootboxTemplate.objects.create(name="Gold Lootbox")
        lootbox = self.inventory.addLootbox(lootbox_template, quantity=1)
        
        self.assertIsNotNone(lootbox)
        self.assertEqual(lootbox.name, "Gold Lootbox")
        self.assertEqual(lootbox.quantity, 1)
        self.assertEqual(lootbox.lootbox_template, lootbox_template)
        self.assertEqual(self.inventory.items.count(), 1)  # Only one lootbox should exist

    def test_add_lootbox_existing(self):
        #Test adding a lootbox when is already in the inv
        lootbox_template = LootboxTemplate.objects.create(name="Gold Lootbox")
        self.inventory.addLootbox(lootbox_template, quantity=1)
        lootbox = self.inventory.addLootbox(lootbox_template, quantity=2)  # Add more
        
        self.assertEqual(lootbox.quantity, 3)  # Quantity should be updated
        self.assertEqual(self.inventory.items.count(), 1)  # Still only one lootbox

"""
TESTING VIEWS
"""


class InventoryViewsTestCase(TestCase):

    def setUp(self):
        # Create a test user for authentication
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com", 
            first_name="Test", 
            last_name="User", 
            password="password123"
        )
        # Create a Client instance for simulating requests
        self.client = Client()

        # Login the test user
        self.client.login(email="testuser@example.com", password="password123")

        # Create an Inventory for the user
        self.inventory = Inventory.objects.create(user=self.user)

        # Create a LootboxTemplate for testing 'open_lootbox'
        self.lootbox_template = LootboxTemplate.objects.create(
            name="Test Lootbox",
            lootbox_image="static/img/lootboxes/test_lootbox.png"
        )

        # Create a LootboxItem and link it via LootboxContents
        self.lootbox_item = LootboxItem.objects.create(
            name="Test Item",
            description="A test item",
            image="static/img/items/test_item.png"
        )

        # Assign a probability so that it can be 'won' from the box
        LootboxContents.objects.create(
            lootbox_template=self.lootbox_template,
            item=self.lootbox_item,
            probability=1.0  # Make it guaranteed for testing
        )

    def test_inventory_view_authenticated(self):
        # Check that logged-in user can access inventory_view
        response = self.client.get(reverse('inventory'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/inventory.html')
        # Check the context contains 'items'
        self.assertIn('items', response.context)
        self.assertEqual(response.context['items'].count(), 0)  
        #Should be 0 because user’s inventory is empty so far

    def test_open_lootbox_requires_post(self):
        # Create a lootbox item in user's inventory
        lootbox = InventoryItem.objects.create(
            inventory=self.inventory,
            name=self.lootbox_template.name,
            item_type=ItemType.LOOTBOX,
            lootbox_template=self.lootbox_template,
            quantity=1
        )

        # Attempt GET request (should fail with error 400)
        url = reverse('open_lootbox', kwargs={'lootbox_id': lootbox.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "POST request required."}
        )

    def test_open_lootbox_not_found(self):
        # Send a POST for a lootbox ID that doesn't exist in this user's inventory
        url = reverse('open_lootbox', kwargs={'lootbox_id': 999})  # Nonexistent ID
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Lootbox not found", str(response.content))

    def test_open_lootbox_empty_contents(self):
        #When a lootbox has no contents, it should respond with no contetnts
        # Create a new lootbox template that has zero items linked
        empty_template = LootboxTemplate.objects.create(
            name="Empty Box",
            lootbox_image="static/img/lootboxes/empty_box.png"
        )

        # Put that empty box into the user's inventory
        empty_box_item = InventoryItem.objects.create(
            inventory=self.inventory,
            name="Empty Box",
            item_type=ItemType.LOOTBOX,
            lootbox_template=empty_template,
            quantity=1
        )

        # Try opening it (POST request)
        url = reverse('open_lootbox', kwargs={'lootbox_id': empty_box_item.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"error": "Lootbox is empty"}
        )

    def test_open_lootbox_success(self):
        # Create an actual lootbox item in user's inventory
        lootbox = InventoryItem.objects.create(
            inventory=self.inventory,
            name=self.lootbox_template.name,
            item_type=ItemType.LOOTBOX,
            lootbox_template=self.lootbox_template,
            quantity=1
        )

        # Confirm user has 1 lootbox, 0 regular items
        self.assertEqual(self.inventory.items.count(), 1)

        # Send a POST to open the lootbox
        url = reverse('open_lootbox', kwargs={'lootbox_id': lootbox.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("item_won", data)
        self.assertEqual(data["item_won"]["name"], "Test Item")
        self.assertTrue(data["lootbox_removed"])  
        # Because quantity goes from 1 to 0 => the item should be removed, so let's check carefully.

        # Reload the lootbox from DB to see updated quantity
        updated_lootbox = InventoryItem.objects.filter(id=lootbox.id).first()
        self.assertIsNone(updated_lootbox)  
        # It should be None, since quantity was decremented to 0 and save() auto-deletes empties

        # Check that user’s inventory now has 1 regular item (the “Test Item”)
        new_items = self.inventory.items.filter(item_type=ItemType.REGULAR)
        self.assertEqual(new_items.count(), 1)
        self.assertEqual(new_items.first().name, "Test Item")