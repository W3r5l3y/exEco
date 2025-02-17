from django.test import TestCase
from django.urls import reverse


class DashboardViewTestCase(TestCase):
    def test_dashboard_view_get(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/dashboard.html")

    def test_dashboard_view_contains_banner(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, 'src="/static/img/dashboard-banner.jpg"')

    def test_dashboard_view_contains_game_cards(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, 'id="game-card-1"')
        self.assertContains(response, 'id="game-card-2"')
        self.assertContains(response, 'id="game-card-3"')
        self.assertContains(response, 'id="game-card-4"')
