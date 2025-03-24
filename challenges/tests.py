from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta
from .models import Challenge, UserChallenge, ChallengeResetTracker
from accounts.models import UserCoins
from django.urls import reverse


class ChallengeResetTestCase(TestCase):
    """Tests for daily and weekly challenge resets."""

    def setUp(self):
        """Set up test data before running tests."""
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="password",
            first_name="Test",
            last_name="User",
        )

        # Create challenges (10 daily, 20 weekly)
        for i in range(1, 11):
            Challenge.objects.create(
                description=f"Daily Challenge {i}",
                reward=10,
                challenge_type="daily",
                goal=1,
            )
        for i in range(1, 21):
            Challenge.objects.create(
                description=f"Weekly Challenge {i}",
                reward=20,
                challenge_type="weekly",
                goal=1,
            )

        # Create ChallengeResetTracker
        self.tracker = ChallengeResetTracker.objects.create(
            last_daily_reset=now() - timedelta(days=1),
            last_weekly_reset=now() - timedelta(days=8),
        )

    def test_daily_challenges_reset(self):
        """Ensure daily challenges reset and are randomized."""
        print(
            "Before Reset Daily Challenges:",
            UserChallenge.objects.filter(user=self.user),
        )

        # Trigger daily reset logic (simulating page load)
        self.client.force_login(self.user)
        self.client.get(reverse("challenges"))  # Visiting the page triggers reset

        # Fetch new daily challenges
        daily_challenges = UserChallenge.objects.filter(
            user=self.user, challenge__challenge_type="daily"
        )
        print("After Reset Daily Challenges:", list(daily_challenges))

        self.assertEqual(len(daily_challenges), 3)  # Ensure 3 challenges are assigned
        self.assertNotEqual(
            daily_challenges[0].challenge.id, daily_challenges[1].challenge.id
        )  # Randomized check

    def test_weekly_challenges_reset(self):
        """Ensure weekly challenges reset and are randomized."""
        print(
            "Before Reset Weekly Challenges:",
            UserChallenge.objects.filter(user=self.user),
        )

        # Trigger weekly reset logic (simulating Monday)
        self.tracker.last_weekly_reset = now() - timedelta(days=8)
        self.tracker.save()
        self.client.force_login(self.user)
        self.client.get(reverse("challenges"))  # Visiting the page triggers reset

        # Fetch new weekly challenges
        weekly_challenges = UserChallenge.objects.filter(
            user=self.user, challenge__challenge_type="weekly"
        )
        print("After Reset Weekly Challenges:", list(weekly_challenges))

        self.assertEqual(
            len(weekly_challenges), 5
        )  # Ensure 5 weekly challenges are assigned
        self.assertNotEqual(
            weekly_challenges[0].challenge.id, weekly_challenges[1].challenge.id
        )  # Randomized check


class AuthenticationTestCase(TestCase):
    """Tests for authentication and access control."""

    def setUp(self):
        """Set up test user."""
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="password",
            first_name="Test",
            last_name="User",
        )

    def test_authenticated_user_access_challenges(self):
        """Ensure a logged-in user can access the challenges page."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("challenges"))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_redirect(self):
        """Ensure unauthenticated users are redirected to the login page."""
        response = self.client.get(reverse("challenges"))
        self.assertEqual(response.status_code, 302)  # Redirect status
        self.assertTrue(response.url.startswith("/login/"))  # Redirects to login page
