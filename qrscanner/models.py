from django.db import models


class Location(models.Model):
    location_code = models.CharField(max_length=4, primary_key=True)
    location_name = models.CharField(max_length=255)
    location_fact = models.TextField()
    cooldown_length = models.IntegerField()  # Cooldown is in minutes
    times_visited = models.IntegerField(default=0)  # Tracks number of scans/visits

    def __str__(self):
        return f"{self.location_name} ({self.location_code})"
