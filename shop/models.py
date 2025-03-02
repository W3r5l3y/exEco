from django.db import models

# Create your models here.
class shopItems(models.Model):
    itemId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="static/img/shop/")
    cost = models.PositiveIntegerField()  # Price in-game currency
    
    def __str__(self):
        return f"{self.name} - {self.cost} coins"