from django.db import models
from django.conf import settings
from django.utils import timezone
import random

class Challenge(models.Model):
    DAILY = 'daily'
    WEEKLY = 'weekly'

    CHALLENGE_TYPES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
    ]

    description = models.CharField(max_length=255)
    reward = models.PositiveIntegerField(default=10)  # Default reward is 10 coins
    challenge_type = models.CharField(max_length=10, choices=CHALLENGE_TYPES)

    def __str__(self):
        return f"{self.description} ({self.challenge_type})"


class UserChallenge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)  # Tracks when the challenge was assigned

    def __str__(self):
        return f"{self.user.email} - {self.challenge.description} - {'Completed' if self.completed else 'Pending'}"

def assign_new_challenges():
    """ Assign new daily and weekly challenges to all users and reset old completions """
    from accounts.models import CustomUser  # Import user model
    from challenges.models import Challenge, UserChallenge

    now = timezone.now()
    daily_challenges = random.sample(list(Challenge.objects.filter(challenge_type="daily")), 3)
    weekly_challenges = random.sample(list(Challenge.objects.filter(challenge_type="weekly")), 5)

    for user in CustomUser.objects.all():
        # Clear old challenges (resets completed state)
        UserChallenge.objects.filter(user=user).delete()

        # Assign new daily challenges
        for challenge in daily_challenges:
            UserChallenge.objects.create(user=user, challenge=challenge)

        # Assign new weekly challenges
        for challenge in weekly_challenges:
            UserChallenge.objects.create(user=user, challenge=challenge)

    print("New challenges assigned to all users!")
