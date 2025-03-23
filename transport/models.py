# transport/models.py
from django.db import models
from accounts.models import CustomUser
from django.conf import settings


class StravaToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="strava_token"
    )
    access_token = models.CharField(
        max_length=200, blank=True, null=True
    )  # The access token (used to make API requests specific to the user)
    refresh_token = models.CharField(
        max_length=200, blank=True, null=True
    )  # The refresh token (used to get a new access token when the current one expires)
    expires_at = models.DateTimeField(
        blank=True, null=True
    )  # The expiry date of the access token
    athlete_id = models.BigIntegerField(
        unique=True, null=True, blank=True
    )  # The Strava athlete ID

    def __str__(self):
        return f"User {self.user.id}'s Strava tokens"


class LoggedActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    activity_id = models.BigIntegerField(unique=True)  # Unique Strava Activity ID
    distance = models.FloatField()  # Distance in meters
    activity_type = models.CharField(
        max_length=20, choices=[("run", "Run"), ("ride", "Ride"), ("walk", "Walk")]
    )  # Run or ride or walk
    option = models.CharField(
        max_length=20, choices=[("commute", "Commute"), ("hobby", "Hobby")]
    )  # Commute or hobby
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"User {self.user.id} - {self.activity_id} - {self.activity_type}"


class CumulativeStats(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="cumulative_stats"
    )
    total_commute_distance = models.FloatField(
        default=0
    )  # Distance in meters (commute)
    total_hobby_distance = models.FloatField(default=0)  # Distance in meters (hobby)

    def __str__(self):
        return f"User {self.user.id} - Commute: {self.total_commute_distance}m, Hobby: {self.total_hobby_distance}m"
