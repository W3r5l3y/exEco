from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import LoginForm, RegisterForm, ChangeProfileForm, ChangePasswordForm
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
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )

    def test_login_register_view_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_register_view_post_login(self):
        response = self.client.post(
            reverse("login"),
            {"email": "test@example.com", "password": "password123", "login": "Login"},
        )
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_register_view_post_invalid_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": "invalid@example.com",
                "password": "wrongpassword",
                "login": "Login",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after invalid login
        self.assertRedirects(
            response, reverse("login") + "?error=Invalid login credentials&tab=login"
        )

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
        self.assertRedirects(response, reverse("login") + "?tab=login")

    def test_login_register_view_post_register_existing_email(self):
        response = self.client.post(
            reverse("login"),
            {
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "password": "password123",
                "confirm_password": "password123",
                "register": "Register",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after registration with existing email
        self.assertRedirects(
            response, reverse("login") + "?error=Email already exists.&tab=register"
        )

    def test_login_register_view_post_register_mismatched_passwords(self):
        response = self.client.post(
            reverse("login"),
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "password123",
                "confirm_password": "password456",
                "register": "Register",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after registration with mismatched passwords
        self.assertRedirects(
            response, reverse("login") + "?error=Passwords do not match.&tab=register"
        )


class AuthenticationBackendTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )

    def test_authenticate_with_email(self):
        backend = EmailBackend()
        user = backend.authenticate(
            request=None, email="test@example.com", password="password123"
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")

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


class WebpageLoadTestCase(TestCase):
    def test_login_page_loads_correctly(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        # Check if specific images are present in the response content
        self.assertContains(response, 'src="/static/img/execo-logo.png"')


class SettingsViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.client.login(email="test@example.com", password="password123")

    def test_settings_view_get(self):
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/settings.html")

    def test_update_profile_success(self):
        response = self.client.post(
            reverse("settings"),
            {
                "confirm_profile": "Confirm",
                "first_name": "Updated",
                "last_name": "User",
                "email": "updated@example.com",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("settings") + "?success=Profile changed successfully"
        )

        user = get_user_model().objects.get(id=self.user.id)
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.email, "updated@example.com")

    def test_update_profile_invalid(self):
        response = self.client.post(
            reverse("settings"),
            {
                "confirm_profile": "Confirm",
                "first_name": "",
                "last_name": "User",
                "email": "updated@example.com",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("settings") + "?error=This field is required."
        )

    def test_change_password_success(self):
        response = self.client.post(
            reverse("settings"),
            {
                "password": "newpassword123",
                "confirm_password": "newpassword123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("settings") + "?success=Password changed successfully"
        )

        user = get_user_model().objects.get(id=self.user.id)
        self.assertTrue(user.check_password("newpassword123"))

    def test_change_password_mismatch(self):
        response = self.client.post(
            reverse("settings"),
            {
                "password": "newpassword123",
                "confirm_password": "differentpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("settings") + "?error=Passwords do not match."
        )
