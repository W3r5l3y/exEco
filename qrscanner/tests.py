from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Location, ScanRecord
from accounts.models import UserPoints
from datetime import timedelta
from django.utils.timezone import now
from inventory.models import Inventory, InventoryItem, LootboxTemplate


class QRScannerTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        UserPoints.objects.create(user=self.user, qrscanner_points=0)
        self.client.login(email="test@example.com", password="password123")
        self.location = Location.objects.create(
            location_code="TEST1",
            location_name="Test Location",
            location_fact="This is a test location.",
            cooldown_length=600,
            times_visited=0,
            location_value=2,
        )

    def test_qrscanner_code_success(self):
        session = self.client.session
        session.save()
        with open("qrscanner/tests/qrtest1.png", "rb") as qr_image:
            response = self.client.post(
                reverse("qrscanner"), {"image": qr_image}, follow=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<strong>Location Name:</strong> <strong>Test Location</strong>"
        )
        self.assertContains(response, "You earned 2 points!")

    def test_qrscanner_code_cooldown(self):
        ScanRecord.objects.create(
            user=self.user, location=self.location, last_scanned=now()
        )
        with open("qrscanner/tests/qrtest1.png", "rb") as qr_image:
            response = self.client.post(
                reverse("qrscanner"), {"image": qr_image}, follow=True
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This QR code is on cooldown.")

    def test_qrscanner_code_location_not_found(self):
        with open("qrscanner/tests/qrtest123.png", "rb") as qr_image:
            response = self.client.post(
                reverse("qrscanner"), {"image": qr_image}, follow=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Location not found for code: test123")

    def test_qrscanner_code_anonymous_user(self):
        self.client.logout()
        with open("qrscanner/tests/qrtest1.png", "rb") as qr_image:
            response = self.client.post(reverse("qrscanner"), {"image": qr_image})
        self.assertEqual(response.status_code, 302)  # Correctly expecting redirect
        self.assertIn("/login/", response.url)

    def test_qrscanner_code_inactive_location(self):
        # Mark the location as inactive
        self.location.is_active = False
        self.location.save()

        with open("qrscanner/tests/qrtest1.png", "rb") as qr_image:
            response = self.client.post(
                reverse("qrscanner"), {"image": qr_image}, follow=True
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This QR code is currently disabled.")

    def test_qrscanner_code_invalid_image(self):
        # Upload an invalid image file
        invalid_image = SimpleUploadedFile("invalid.txt", b"Not an image file")
        response = self.client.post(
            reverse("qrscanner"), {"image": invalid_image}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
        )


def test_qrscanner_code_multiple_scans(self):
    # Simulate multiple scans of the same QR code
    with open("qrscanner/tests/qrtest1.png", "rb") as qr_image:
        # First scan should be successful
        response = self.client.post(
            reverse("qrscanner"), {"image": qr_image}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You earned 2 points!")

        # Reset the file pointer for next read
        qr_image.seek(0)

        # Second scan should be on cooldown
        response = self.client.post(
            reverse("qrscanner"), {"image": qr_image}, follow=True
        )

    # Check for the cooldown message
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "This QR code is on cooldown")

    # Verify the location was visited once
    location = Location.objects.get(location_code="TEST1")
    self.assertEqual(location.times_visited, 2)


class QRScannerLeaderboardTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.client.login(email="test@example.com", password="password123")

    def test_qrscanner_leaderboard_view_get(self):
        response = self.client.get(reverse("qrscanner"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "qrscanner/qrscanner.html")

    def test_qrscanner_leaderboard_view_contains_leaderboard(self):
        response = self.client.get(reverse("qrscanner"))
        self.assertContains(response, 'id="leaderboard-list"')
        for i in range(1, 11):
            self.assertContains(response, f'id="leaderboard-item-{i}"')

    def test_qrscanner_leaderboard_data(self):
        # Create some user points for testing
        for i in range(1, 16):  # Create 15 users
            user = get_user_model().objects.create_user(
                email=f"user{i}@test.com",
                first_name=f"User{i}",
                last_name=f"Test{i}",
                password="password123",
            )
            UserPoints.objects.create(
                user=user,
                qrscanner_points=i * 3,
            )
        # Get the leaderboard data
        response = self.client.get(reverse("get_qrscanner_leaderboard"))
        self.assertEqual(response.status_code, 200)
        # Check that the top 10 users are in the response
        for i in range(6, 16):
            self.assertContains(response, f"User{i} Test{i}")
            self.assertContains(response, f"{i * 3}")


class LocationTestCase(TestCase):
    def test_add_new_location(self):
        # Test that adding a new location works correctly
        location = Location.addLocation(
            location_code="L001",
            location_name="Bin by forum",
            location_fact="Pretty nice bin",
            cooldown_length=180,
            location_value=10,
        )

        # Ensure a location object is returned
        self.assertIsInstance(location, Location)
        self.assertEqual(location.location_code, "L001")
        self.assertEqual(location.location_name, "Bin by forum")
        self.assertEqual(location.location_fact, "Pretty nice bin")
        self.assertEqual(location.cooldown_length, 180)
        self.assertEqual(location.location_value, 10)

        # Ensure the location is in the database
        self.assertTrue(Location.objects.filter(location_code="L001").exists())

    def test_add_duplicate_location(self):
        # Test if location code already exists returns -1
        # Create initial location
        Location.objects.create(
            location_code="L002",
            location_name="The buisness block male toilets",
            location_fact="Smelly",
            cooldown_length=300,
            location_value=15,
        )

        # Try to add the same location again
        result = Location.addLocation(
            location_code="L002",
            location_name="The buisness block male toilets",
            location_fact="Smelly",
            cooldown_length=300,
            location_value=15,
        )

        # Ensure it returns -1 for a duplicate location
        self.assertEqual(result, "Code already exists")

        # Ensure only one instance exists in the database
        self.assertEqual(Location.objects.filter(location_code="L002").count(), 1)

    def test_location_is_active(self):
        # Create a location with is_active set to True
        active_location = Location.objects.create(
            location_code="L003",
            location_name="Active Location",
            location_fact="This location is active.",
            cooldown_length=120,
            location_value=5,
            is_active=True,
        )

        # Create a location with is_active set to False
        inactive_location = Location.objects.create(
            location_code="L004",
            location_name="Inactive Location",
            location_fact="This location is inactive.",
            cooldown_length=120,
            location_value=5,
            is_active=False,
        )

        # Ensure the active location is active
        self.assertTrue(active_location.is_active)

        # Ensure the inactive location is not active
        self.assertFalse(inactive_location.is_active)

        # Ensure the locations are in the database
        self.assertTrue(Location.objects.filter(location_code="L003").exists())
        self.assertTrue(Location.objects.filter(location_code="L004").exists())
