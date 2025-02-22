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

    def test_scan_qr_code_success(self):
        with open("qrscanner/tests/qr0001.png", "rb") as qr_image:
            response = self.client.post(reverse("scan_qr"), {"image": qr_image})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "QR Code Data: 0001")
        self.assertContains(response, "Location Name: Test Location")
        self.assertContains(response, "Fact: This is a test location.")
        self.assertContains(response, "Times Scanned: 1")
        self.assertContains(response, "Point Value: 2")
        self.assertContains(response, "Total Points: 2")

    def test_scan_qr_code_cooldown(self):
        ScanRecord.objects.create(
            user=self.user, location=self.location, last_scanned=now()
        )
        with open("qrscanner/tests/qr0001.png", "rb") as qr_image:
            response = self.client.post(reverse("scan_qr"), {"image": qr_image})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This QR code is on cooldown.")

    def test_scan_qr_code_location_not_found(self):
        with open("qrscanner/tests/qr0002.png", "rb") as qr_image:
            response = self.client.post(reverse("scan_qr"), {"image": qr_image})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Location not found for code: 0002")

    def test_scan_qr_code_anonymous_user(self):
        self.client.logout()
        with open("qrscanner/tests/qr0001.png", "rb") as qr_image:
            response = self.client.post(reverse("scan_qr"), {"image": qr_image})
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, "/login/?next=/qrscanner/")
