# transport/models.py
from django.db import models
from django.conf import settings  # So we can reference AUTH_USER_MODEL

class StravaToken(models.Model):
    """
    Stores a user's Strava tokens (access token, refresh token, expiry).
    Linked to your custom user model via a OneToOneField.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, # Use the custom user model from accounts app
        on_delete=models.CASCADE, # If the user is deleted, delete the token
        related_name='strava_token'
    )
    access_token = models.CharField(max_length=200, blank=True, null=True) # The access token (used to make API requests specific to the user)
    refresh_token = models.CharField(max_length=200, blank=True, null=True) # The refresh token (used to get a new access token when the current one expires)
    expires_at = models.DateTimeField(blank=True, null=True) # The expiry date of the access token
    athlete_id = models.BigIntegerField(unique=True, null=True, blank=True) # The Strava athlete ID

    def __str__(self):
        return f"{self.user.email}'s Strava tokens"
