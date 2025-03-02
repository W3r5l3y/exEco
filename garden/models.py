from django.db import models
from accounts.models import CustomUser

class GardenState(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to user
    state = models.JSONField(default=dict)  # Store garden state as JSON
    updated_at = models.DateTimeField(auto_now=True)  # Track last update

    def __str__(self):
        return f"GardenState for User ID {self.user.id}"