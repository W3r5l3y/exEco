from django.db import models
from accounts.models import CustomUser
# Create your models here.

# The table for bins
class Bins(models.Model):
    bin_id = models.AutoField(primary_key=True)
    bin_name = models.CharField(max_length=100)
    bin_image = models.ImageField(upload_to="static/img/bins/")

# The table for items
class Items(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=100)
    item_image = models.ImageField(upload_to="static/img/items/")
    bin_id = models.ForeignKey(Bins, on_delete=models.CASCADE)


class BinLeaderboardEntry(models.Model):
    """Tracks points earned by each player for leaderboard ranking."""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="leaderboard_entry")
    user_score = models.IntegerField(default=0)

    def __str__(self):
        return f"User {self.user.id} - {self.points} points"