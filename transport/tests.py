from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .models import StravaToken, LoggedActivity, CumulativeStats
from accounts.models import UserPoints
import json


class TransportAppTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.client.login(email="test@example.com", password="password123")

    def test_get_transport_leaderboard(self):
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
                transport_points=i * 10,
            )

        response = self.client.get(reverse("get_transport_leaderboard"))
        self.assertEqual(response.status_code, 200)
        leaderboard_data = response.json()
        self.assertEqual(len(leaderboard_data), 10)
        # Only top 10 users should be displayed
        expected_order = [
            {"username": "User15 Test15", "transport_points": 150},
            {"username": "User14 Test14", "transport_points": 140},
            {"username": "User13 Test13", "transport_points": 130},
            {"username": "User12 Test12", "transport_points": 120},
            {"username": "User11 Test11", "transport_points": 110},
            {"username": "User10 Test10", "transport_points": 100},
            {"username": "User9 Test9", "transport_points": 90},
            {"username": "User8 Test8", "transport_points": 80},
            {"username": "User7 Test7", "transport_points": 70},
            {"username": "User6 Test6", "transport_points": 60},
        ]
        for entry, expected in zip(leaderboard_data, expected_order):
            self.assertEqual(entry["username"], expected["username"])
            self.assertEqual(entry["transport_points"], expected["transport_points"])

    def test_log_activity(self):
        # Log an activity
        activity_data = {
            "activity_id": "123456789",
            "distance": 5000,  # 5 km
            "activity_type": "run",
            "option": "commute",
        }
        response = self.client.post(
            reverse("log_activity"),
            data=json.dumps(activity_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], "Activity logged successfully!")

        # Check if the activity was logged
        logged_activity = LoggedActivity.objects.get(activity_id="123456789")
        self.assertEqual(logged_activity.user, self.user)
        self.assertEqual(logged_activity.distance, 5000)
        self.assertEqual(logged_activity.activity_type, "run")
        self.assertEqual(logged_activity.option, "commute")

        # Check if the cumulative stats were updated
        cumulative_stats = CumulativeStats.objects.get(user=self.user)
        self.assertEqual(cumulative_stats.total_commute_distance, 5000)

        # Check if the user points were updated
        user_points = UserPoints.objects.get(user=self.user)
        self.assertEqual(user_points.transport_points, 50)  # 10 points per 1 km

    def test_get_transport_stats(self):
        # Create cumulative stats and user points for the user
        CumulativeStats.objects.create(
            user=self.user,
            total_commute_distance=12500,  # 12.5 km
            total_hobby_distance=7500,  # 7.5 km
        )
        UserPoints.objects.create(
            user=self.user,
            transport_points=200,
        )

        response = self.client.get(reverse("get_transport_stats"))
        self.assertEqual(response.status_code, 200)
        stats_data = response.json()
        self.assertEqual(stats_data["total_commute_distance"], 12500)
        self.assertEqual(stats_data["total_hobby_distance"], 7500)
        self.assertEqual(stats_data["points_earned"], 200)

    def test_points_calculation_from_cumulative_stats(self):
        # Create cumulative stats for the user
        CumulativeStats.objects.create(
            user=self.user,
            total_commute_distance=10000,  # 10 km
            total_hobby_distance=5000,  # 5 km
        )
        UserPoints.objects.create(
            user=self.user,
            transport_points=150,
        )

        # Log multiple activities
        activities = [
            {
                "activity_id": "1",
                "distance": 3000,
                "activity_type": "run",
                "option": "commute",
            },
            {
                "activity_id": "2",
                "distance": 2000,
                "activity_type": "bike",
                "option": "commute",
            },
            {
                "activity_id": "3",
                "distance": 4000,
                "activity_type": "walk",
                "option": "hobby",
            },
        ]
        for activity in activities:
            self.client.post(
                reverse("log_activity"),
                data=json.dumps(activity),
                content_type="application/json",
            )

        # Check if the cumulative stats were updated
        cumulative_stats = CumulativeStats.objects.get(user=self.user)
        self.assertEqual(
            cumulative_stats.total_commute_distance, 15000
        )  # Initial 10 km + 3 km + 2 km
        self.assertEqual(
            cumulative_stats.total_hobby_distance, 9000
        )  # Initial 5 km + 4 km

        # Check if the user points were updated
        user_points = UserPoints.objects.get(user=self.user)
        self.assertEqual(
            user_points.transport_points, 240
        )  # Initial 150 points + 30 points + 20 points + 40 points
