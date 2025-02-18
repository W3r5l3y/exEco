from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.templatetags.static import static


class DashboardViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.client.login(email="test@example.com", password="password123")

    def test_dashboard_view_get(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/dashboard.html")

    def test_dashboard_view_contains_banner(self):
        response = self.client.get(reverse("dashboard"))
        banner_url = static("img/dashboard-banner.jpg")
        self.assertContains(response, f'src="{banner_url}"')

    def test_dashboard_view_contains_game_cards(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, 'id="game-card-1"')
        self.assertContains(response, 'id="game-card-2"')
        self.assertContains(response, 'id="game-card-3"')
        self.assertContains(response, 'id="game-card-4"')
