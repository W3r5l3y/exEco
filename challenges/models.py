from django.db import models
from django.conf import settings
import random

class Challenge(models.Model):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    CHALLENGE_TYPE_CHOICES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
    ]
    
    description = models.TextField()
    points = models.IntegerField()
    challenge_type = models.CharField(
        max_length=10, choices=CHALLENGE_TYPE_CHOICES
    )
    
    def __str__(self):
        return f"{self.description} ({self.challenge_type})"
    
    @staticmethod
    def get_random_challenge(challenge_type):
        challenges = Challenge.objects.filter(challenge_type=challenge_type)
        return random.choice(challenges) if challenges.exists() else None

class UserChallenge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.description} - {'Completed' if self.completed else 'Pending'}"
    
    @staticmethod
    def assign_new_challenge(user, challenge_type):
        challenge = Challenge.get_random_challenge(challenge_type)
        if challenge:
            user_challenge = UserChallenge.objects.create(user=user, challenge=challenge)
            return user_challenge
        return None