from django.db import models


# Create your models here.
class ShopItems(models.Model):
    itemId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="shop/", blank=True, null=True)
    cost = models.PositiveIntegerField()  # Price in-game currency
    aesthetic_appeal = models.IntegerField(default=0)
    habitat = models.IntegerField(default=0)
    carbon_uptake = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.cost} coins"
