from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Location, ScanRecord
from accounts.models import UserPoints
from datetime import timedelta
from django.utils.timezone import now


class QRScannerTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.client.login(email="test@example.com", password="password123")
        self.location = Location.objects.create(
            location_code="0001",
            location_name="Test Location",
            location_fact="This is a test location.",
            cooldown_length=60,
            times_visited=0,
            location_value=2,
        )

    def test_qrscanner_code_success(self):
        session = self.client.session
        session.save()
        with open("qrscanner/tests/qr0001.png", "rb") as qr_image:
            response = self.client.post(reverse("qrscanner"), {'image': qr_image}, follow=True)  
        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, "<strong>Location Name:</strong> <strong>Test Location</strong>")
        self.assertContains(response, "You earned 2 points!")

    def test_qrscanner_code_cooldown(self):
        ScanRecord.objects.create(
            user=self.user, location=self.location, last_scanned=now()
        )
        with open("qrscanner/tests/qr0001.png", "rb") as qr_image:
            response = self.client.post(reverse('qrscanner'), {'image': qr_image}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This QR code is on cooldown.")

    def test_qrscanner_code_location_not_found(self):
        with open("qrscanner/tests/qr0002.png", "rb") as qr_image:
            response = self.client.post(reverse('qrscanner'), {'image': qr_image}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Location not found for code: 0002")


    def test_qrscanner_code_anonymous_user(self):
        self.client.logout()
        with open("qrscanner/tests/qr0001.png", "rb") as qr_image:
            response = self.client.post(reverse('qrscanner'), {'image': qr_image}) 
        self.assertEqual(response.status_code, 302)  # Correctly expecting redirect
        self.assertIn('/login/', response.url)


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
