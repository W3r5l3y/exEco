from django.db import models
from accounts.models import CustomUser

# Create your models here.


# The table for bins
class Bins(models.Model):
    bin_id = models.AutoField(primary_key=True)
    bin_name = models.CharField(max_length=100)
    bin_image = models.ImageField(upload_to="static/img/bins/")

    def __init__(self):
        return f"{self.bin_name} with image held as {self.bin_image}"
# The table for items
class Items(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=100)
    item_image = models.ImageField(upload_to="static/img/items/")
    bin_id = models.ForeignKey(Bins, on_delete=models.CASCADE)
    
    def __init__(self):
        return f"{self.item_name} goes in {self.bin_id.bin_name}, with image held as {self.item_image}"
