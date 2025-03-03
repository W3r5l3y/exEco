from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from .models import GardenState
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
        new_state = {"plants": ["Orchid", "Lavender"]}
        response = self.client.post(
            url, data=json.dumps({"state": new_state}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"message": "Garden saved successfully!"})

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