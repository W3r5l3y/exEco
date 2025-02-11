from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .forms import LoginForm, RegisterForm
from .backends import EmailBackend


class FormsTestCase(TestCase):
    def test_login_form_valid(self):
        form_data = {"email": "test@example.com", "password": "password123"}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form_valid(self):
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form_invalid(self):
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "confirm_password": "password456",  # Passwords do not match
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())


class ViewsTestCase(TestCase):
    def test_login_register_view_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    # Uncomment the following test after implementing the home view
    """ 
    def test_login_register_view_post_login(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )
        response = self.client.post(
            reverse("login"),
            {"email": "test@example.com", "password": "password123", "login": "Login"},
        )
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertRedirects(response, reverse("home"))
    """

    def test_login_register_view_post_register(self):
        response = self.client.post(
            reverse("login"),
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "password123",
                "confirm_password": "password123",
                "register": "Register",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        self.assertRedirects(response, reverse("login"))


class AuthenticationBackendTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

    # Uncomment the following test after implementing the authentication with datbase
    """
    def test_authenticate_with_email(self):
        backend = EmailBackend()
        user = backend.authenticate(
            request=None, email="test@example.com", password="password123"
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")
    """

    def test_authenticate_with_invalid_email(self):
        backend = EmailBackend()
        user = backend.authenticate(
            request=None, email="invalid@example.com", password="password123"
        )
        self.assertIsNone(user)

    def test_authenticate_with_invalid_password(self):
        backend = EmailBackend()
        user = backend.authenticate(
            request=None, email="test@example.com", password="wrongpassword"
        )
        self.assertIsNone(user)
