from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from qrscanner.models import Location
from accounts.models import CustomUser
from django.contrib.auth import get_user_model
from transport.models import StravaToken
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
            password="password123"
        )
        self.user.is_staff = True
        self.user.save()
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

class StravaLinkTests(TestCase):

    def setUp(self):
        # Setup test client and users
        self.client = Client()
        self.user1 = get_user_model().objects.create_user(
            email="user1@example.com",
            first_name="User",
            last_name="One",
            password="password123"
        )
        self.user2 = get_user_model().objects.create_user(
            email="user2@example.com",
            first_name="User",
            last_name="Two",
            password="password123"
        )

        # URL for get_strava_links API
        self.strava_links_url = reverse("get_strava_links")

    def test_no_strava_links(self):
        # Test if API returns no linked accounts, when there are no linked accounts
        response = self.client.get(self.strava_links_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "No linked Strava accounts found"})

    def test_one_user_with_strava(self):
        # Test view with a user in the database with a linked Strava account
        StravaToken.objects.create(user=self.user1, access_token="token1")

        response = self.client.get(self.strava_links_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("strava_links", response.json())
        self.assertEqual(response.json()["strava_links"], [self.user1.id])

    def test_multiple_users_with_strava(self):
        # Test view with multiple users,and that it passed in the correct user IDs
        StravaToken.objects.create(user=self.user1, access_token="token1")
        StravaToken.objects.create(user=self.user2, access_token="token2")

        response = self.client.get(self.strava_links_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("strava_links", response.json())

        # Check that both user IDs are returned
        expected_ids = [self.user1.id, self.user2.id]
        self.assertCountEqual(response.json()["strava_links"], expected_ids)


class QRScannerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="password123"
        )
        self.client.login(email="test@example.com", password="password123")

    def test_add_location_to_qr(self):
        url = reverse("add_location_to_qr", kwargs={
            "location_code": "L123",
            "location_name": "The forum",
            "location_fact": "A nice area",
            "cooldown_length": 120,
            "location_value": 10
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("qr_code_url", response.json())

    def test_get_qr_codes(self):
        Location.objects.create(location_code="L123", location_name="Test Park", is_active=True)
        url = reverse("get_qr_codes")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("qr_codes", response.json())

