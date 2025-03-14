from django.utils.timezone import now
from django.db import models
from django.conf import settings

class Challenge(models.Model):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    LIFETIME = 'lifetime'
    CHALLENGE_TYPES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (LIFETIME, 'Lifetime'),
    ]

    GAME_CATEGORIES = [
        ('bingame', 'Bin Game'),
        ('transport', 'Transport'),
        ('qrscanner', 'QR Scanner'),
        ('forum', 'Forum'),
        ('general', 'General'),
        ('lifetime', 'Lifetime'),
    ]

    description = models.CharField(max_length=255)
    reward = models.PositiveIntegerField(default=10)
    challenge_type = models.CharField(max_length=10, choices=CHALLENGE_TYPES)
    game_category = models.CharField(max_length=20, choices=GAME_CATEGORIES, default="general")
    goal = models.IntegerField(default=1)  # The target number required to complete the challenge

    def __str__(self):
        return f"{self.description} ({self.challenge_type} - {self.game_category})"


class UserChallenge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    progress = models.IntegerField(default=0)  # Track how far the user has progressed toward completion

    def __str__(self):
        return f"{self.user.email} - {self.challenge.description} - {self.progress}/{self.challenge.goal} {'(Completed)' if self.completed else '(In Progress)'}"

    def update_progress(self, amount=1):
        """ Increments progress and checks for completion """
        if not self.completed:
            self.progress += amount
            if self.progress >= self.challenge.goal:
                self.progress = self.challenge.goal
                self.completed = True
                self.reward_user()
            self.save()

    def reward_user(self):
        """ Rewards the user when the challenge is completed """
        from accounts.models import UserCoins
        user_coins, created = UserCoins.objects.get_or_create(user=self.user)
        user_coins.coins += self.challenge.reward
        user_coins.save()

class ChallengeResetTracker(models.Model):
    last_daily_reset = models.DateTimeField(default=now)
    last_weekly_reset = models.DateTimeField(default=now)

    @classmethod
    def get_reset_tracker(cls):
        """Fetch the reset tracker or create one if missing."""
        tracker, created = cls.objects.get_or_create(id=1)
        return tracker