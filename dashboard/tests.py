from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.templatetags.static import static
from accounts.models import UserPoints


class DashboardViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.client.login(email="test@example.com", password="password123")

        # Create some user points for testing
        for i in range(1, 16):  # Create 15 users
            user = get_user_model().objects.create_user(
                email=f"user{i}@example.com",
                first_name=f"User{i}",
                last_name=f"Test{i}",
                password="password123",
            )
            UserPoints.objects.create(
                user=user,
                bingame_points=i * 1,
                qrscanner_points=i * 3,
                transport_points=i * 5,
            )

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

    def test_dashboard_view_contains_leaderboard(self):
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, 'id="leaderboard-list"')
        for i in range(1, 11):
            # Only check for the top 10 items
            self.assertContains(response, f'id="leaderboard-item-{i}"')

    def test_leaderboard_data(self):
        response = self.client.get(reverse("get_total_leaderboard"))
        self.assertEqual(response.status_code, 200)
        leaderboard_data = response.json()
        self.assertEqual(len(leaderboard_data), 10)
        # Only top 10 users should be displayed
        expected_order = [
            {"username": "User15 Test15", "total_points": 135},  # 15 * (1 + 3 + 5)
            {"username": "User14 Test14", "total_points": 126},
            {"username": "User13 Test13", "total_points": 117},
            {"username": "User12 Test12", "total_points": 108},
            {"username": "User11 Test11", "total_points": 99},
            {"username": "User10 Test10", "total_points": 90},
            {"username": "User9 Test9", "total_points": 81},
            {"username": "User8 Test8", "total_points": 72},
            {"username": "User7 Test7", "total_points": 63},
            {"username": "User6 Test6", "total_points": 54},
        ]
        for entry, expected in zip(leaderboard_data, expected_order):
            self.assertEqual(entry["username"], expected["username"])
            self.assertEqual(entry["total_points"], expected["total_points"])
