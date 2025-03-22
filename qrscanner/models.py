from django.db import models
from django.conf import settings
from django.utils.timezone import now


class Location(models.Model):
    location_code = models.CharField(max_length=4, primary_key=True)
    location_name = models.CharField(max_length=255)
    location_fact = models.TextField()
    cooldown_length = models.IntegerField()  # Cooldown is in seconds
    times_visited = models.IntegerField(default=0)  # Tracks number of scans/visits
    location_value = models.IntegerField(default=1)  # Amount of points awarded
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="qrscanner/locations/", blank=True, null=True)

    @classmethod
    def addLocation(
        cls,
        location_code,
        location_name,
        location_fact,
        cooldown_length=0,
        location_value=5,
        image=None,
    ):
        location, created = cls.objects.get_or_create(
            location_code=location_code,
            defaults={
                "location_name": location_name,
                "location_fact": location_fact,
                "cooldown_length": cooldown_length,
                "location_value": location_value,
                "image": image,
            },
        )

        if not created:
            return "Code already exists"  # Location already exists
        return location

    def __str__(self):
        return f"{self.location_name} ({self.location_value} points)"


class ScanRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    last_scanned = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "user",
            "location",
        )  # Prevent duplicate scans within cooldown

    def __str__(self):
        return f"{self.user.email} scanned {self.location.location_name} at {self.last_scanned}"
