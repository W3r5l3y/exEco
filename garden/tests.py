from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from .models import GardenState
from inventory.models import InventoryItem, Inventory
import json

# Create your tests here.
"""
MODELS TESTING
"""

class GardenModelTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="password123"
        )

        # Create an initial garden state
        self.garden = GardenState.objects.create(
            user=self.user,
            state={"plants": ["Rose", "Sunflower"]}
        )

    def test_garden_creation(self):
        # Ensure garden state is stored correctly
        self.assertEqual(self.garden.user.email, "testuser@example.com")
        self.assertEqual(self.garden.state, {"plants": ["Rose", "Sunflower"]})

    def test_garden_str_method(self):
        # Check string representation
        self.assertEqual(str(self.garden), f"GardenState for User ID {self.user.id}")

    def test_garden_state_update(self):
        # Test updating garden state
        self.garden.state = {"plants": ["Cactus", "Lily"]}
        self.garden.save()
        self.garden.refresh_from_db()
        self.assertEqual(self.garden.state, {"plants": ["Cactus", "Lily"]})
        

class GardenStateTests(TestCase):

    def setUp(self):
        # Set up test user and a inventory
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="password123"
        )

        # Create test inventory for the user
        self.inventory = Inventory.objects.create(user=self.user)

        # Create test inventory items with stats
        self.item1 = InventoryItem.objects.create(
            inventory=self.inventory,
            name="Tree",
            item_type="regular",
            aesthetic_appeal=5,
            habitat=4,
            carbon_uptake=10,
            waste_reduction=2,
            health_of_garden=3,
            innovation=1
        )
        self.item2 = InventoryItem.objects.create(
            inventory=self.inventory,
            name="Flower",
            item_type="regular",
            aesthetic_appeal=7,
            habitat=6,
            carbon_uptake=2,
            waste_reduction=1,
            health_of_garden=5,
            innovation=3
        )

        # Create a garden state containing these items
        self.garden = GardenState.objects.create(
            user=self.user,
            state={
                "3-7": f"inventory-item-{self.item1.id}-1",
                "6-5": f"inventory-item-{self.item2.id}-1"
            }
        )

    def test_calculate_stats(self):
        # Test that calculate_stats returns the correct values
        stats = self.garden.calculate_stats()

        expected_avg_stats = {
            "aesthetic_appeal": 6,
            "habitat": 5,
            "carbon_uptake": 6,
            "waste_reduction": 1.5,
            "health_of_garden": 4,
            "innovation": 2
        }
        expected_total_stat = sum(expected_avg_stats.values())

        self.assertEqual(stats["average_stats"], expected_avg_stats)
        self.assertEqual(stats["total_stats"], expected_total_stat)

    def test_calculate_stats_empty_garden(self):
        # Test it handles an empty garden
        empty_garden = GardenState.objects.create(user=self.user, state={})
        stats = empty_garden.calculate_stats()

        expected_avg_stats = {
            "aesthetic_appeal": 0,
            "habitat": 0,
            "carbon_uptake": 0,
            "waste_reduction": 0,
            "health_of_garden": 0,
            "innovation": 0
        }
        expected_total_stat = 0

        self.assertEqual(stats["average_stats"], expected_avg_stats)
        self.assertEqual(stats["total_stats"], expected_total_stat)



"""
VIEWS TESTING
"""

class GardenViewsTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="password123"
        )

        # Create a Client instance for simulating requests
        self.client = Client()
        self.client.login(email="testuser@example.com", password="password123")

        # Create a garden state
        self.garden = GardenState.objects.create(
            user=self.user,
            state={"plants": ["Tulip"]}
        )

    def test_garden_view(self):
        # Test if the garden page loads successfully
        response = self.client.get(reverse('garden'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'garden/garden.html')

    def test_load_garden_existing(self):
        # Test loading garden state when it exists
        response = self.client.get(reverse('load_garden'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"state": {"plants": ["Tulip"]}})

    def test_load_garden_empty(self):
        # Remove garden state to simulate a new user
        self.garden.delete()

        response = self.client.get(reverse('load_garden'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"state": {}})

    def test_save_garden_success(self):
        # Test saving a new garden state
        url = reverse('save_garden')
        new_state = {"3-7": "inventory-item-2-1", "6-5": "inventory-item-3-1"}

        response = self.client.post(
            url, data=json.dumps({"state": new_state}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        # Ensure response contains the expected keys
        response_data = json.loads(response.content.decode())
        self.assertIn("message", response_data)
        self.assertIn("average_stats", response_data)
        self.assertIn("total_stat", response_data)

        # Ensure the message is correct
        self.assertEqual(response_data["message"], "Garden saved successfully!")

        # Ensure average stats are returned and initialized to zero (since no real inventory data in test DB)
        expected_avg_stats = {
            "aesthetic_appeal": 0,
            "habitat": 0,
            "carbon_uptake": 0,
            "waste_reduction": 0,
            "health_of_garden": 0,
            "innovation": 0
        }
        self.assertEqual(response_data["average_stats"], expected_avg_stats)
        self.assertEqual(response_data["total_stat"], 0)

        # Check if the garden state was updated
        self.garden.refresh_from_db()
        self.assertEqual(self.garden.state, new_state)


    def test_save_garden_invalid_json(self):
        # Test invalid JSON data
        url = reverse('save_garden')
        response = self.client.post(url, data="invalid data", content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Invalid JSON data"})

    def test_save_garden_invalid_method(self):
        # Test sending a GET request to save_garden (should fail)
        response = self.client.get(reverse('save_garden'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Invalid request method"})
        
    