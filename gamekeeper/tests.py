from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from qrscanner.models import Location
from accounts.models import CustomUser
from django.contrib.auth import get_user_model
#from .views import add_location_to_qr
import os

class QRCodeGenerationTests(TestCase):

    def setUp(self):
        # Setup test and user client
        self.client = Client()
        
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.client.login(email="test@example.com", password="password123")

        # Mock location data
        self.location_data = {
            "location_code": "L123",
            "location_name": "Test Park",
            "location_fact": "A scenic park with lakes.",
            "cooldown_length": 120,
            "location_value": 10,
        }
        
        # Generate the correct URL with arguments
        self.qr_code_url = reverse(
            'add_location_to_qr',
            kwargs={
                "location_code": self.location_data["location_code"],
                "location_name": self.location_data["location_name"],
                "location_fact": self.location_data["location_fact"],
                "cooldown_length": self.location_data["cooldown_length"],
                "location_value": self.location_data["location_value"],
            }
        )

    def test_generate_qr_code_success(self):
        # Test if qr code is generated and stored correctly

        # Make request to add location and generate QR code
        response = self.client.get(self.qr_code_url, self.location_data)

        # Check for a successful response
        self.assertEqual(response.status_code, 200)
        self.assertIn("qr_code_url", response.json())

        # Extract QR code URL from response
        qr_code_url = response.json()["qr_code_url"]
        qr_code_path = os.path.join(settings.MEDIA_ROOT, "qr_codes", f"{self.location_data['location_code']}.png")

        # Check if QR code file exists
        self.assertTrue(os.path.exists(qr_code_path))

    def test_generate_qr_code_duplicate_location(self):
        # Test that adding duplicated qr code doesnt work

        # Create a location first
        Location.addLocation(**self.location_data)

        # Try adding the same location again
        response = self.client.get(self.qr_code_url, self.location_data)

        # Should return an error response
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["error"], "Code already exists")

    def tearDown(self):
        # Cleanup test qr codes
        qr_code_path = os.path.join(settings.MEDIA_ROOT, "qr_codes", f"{self.location_data['location_code']}.png")
        if os.path.exists(qr_code_path):
            os.remove(qr_code_path)
