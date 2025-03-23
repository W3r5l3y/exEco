from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import ContactMessage
import json


class ContactModelTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )

        # Create a test message
        self.message = ContactMessage.objects.create(
            user=self.user, message="testy 123"
        )

    def test_message_creation(self):
        # Test if the message was created correctly
        self.assertEqual(self.message.user.email, "testuser@example.com")
        self.assertEqual(self.message.message, "testy 123")
        self.assertFalse(self.message.complete)
        self.assertIsNone(self.message.response)

    def test_message_str(self):
        # Test the string representation of the message
        self.assertIn(f"Message from {self.user.email}", str(self.message))


class ContactViewsTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )

        # Create a client for testing
        self.client = Client()

    def test_contact_view(self):
        # Test if the contact page loads correctly
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact/contact.html")

    def test_submit_message_unauthenticated(self):
        # Test that unauthenticated users are redirected to login
        response = self.client.post(
            reverse("submit_contact_message"),
            data=json.dumps({"message": "Test message"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)  # Redirect status
        self.assertIn("login", response.url)

    def test_submit_message_authenticated(self):
        # Login the test user
        self.client.login(email="testuser@example.com", password="password123")

        # Submit a valid message
        response = self.client.post(
            reverse("submit_contact_message"),
            data=json.dumps({"message": "Help, I'm having an issue!"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"status": "success", "message": "Message submitted"},
        )

        # Check that the message was created in the database
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(
            ContactMessage.objects.first().message, "Help, I'm having an issue!"
        )

    def test_submit_empty_message(self):
        # Login the test user
        self.client.login(email="testuser@example.com", password="password123")

        # Submit an empty message
        response = self.client.post(
            reverse("submit_contact_message"),
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"status": "error", "message": "No message provided"},
        )

        # Check that no message was created
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_submit_invalid_json(self):
        # Login the test user
        self.client.login(email="testuser@example.com", password="password123")

        # Submit invalid JSON data
        response = self.client.post(
            reverse("submit_contact_message"),
            data="This is not JSON",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {"status": "error", "message": "Invalid JSON"},
        )

        # Check that no message was created
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_submit_wrong_method(self):
        # Login the test user
        self.client.login(email="testuser@example.com", password="password123")

        # Try with GET instead of POST
        response = self.client.get(reverse("submit_contact_message"))

        # Should return 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)
