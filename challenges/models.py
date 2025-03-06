from django.db import models
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
    reward = models.PositiveIntegerField()
    challenge_type = models.CharField(max_length=10, choices=CHALLENGE_TYPES)
    active = models.BooleanField(default=False)
    last_assigned = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.description} ({self.challenge_type})"

    @classmethod
    def refresh_challenges(cls):
        """ Refresh daily and weekly challenges based on their type. """
        now = timezone.now()
        daily_reset_time = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        weekly_reset_time = daily_reset_time + timezone.timedelta(days=(7 - daily_reset_time.weekday()))  # Next Monday

        # Refresh daily challenges
        if now >= daily_reset_time:
            cls.objects.filter(challenge_type=cls.DAILY).update(active=False)  # Deactivate old challenges
            new_daily_challenges = random.sample(list(cls.objects.filter(challenge_type=cls.DAILY)), 3)
            for challenge in new_daily_challenges:
                challenge.active = True
                challenge.last_assigned = now
                challenge.save()

        # Refresh weekly challenges
        if now >= weekly_reset_time:
            cls.objects.filter(challenge_type=cls.WEEKLY).update(active=False)  # Deactivate old challenges
            new_weekly_challenges = random.sample(list(cls.objects.filter(challenge_type=cls.WEEKLY)), 5)
            for challenge in new_weekly_challenges:
                challenge.active = True
                challenge.last_assigned = now
                challenge.save()
