from django.db import models
from accounts.models import CustomUser
from inventory.models import InventoryItem

class GardenState(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to user
    state = models.JSONField(default=dict)  # Store garden state as JSON
    updated_at = models.DateTimeField(auto_now=True)  # Track last update

    
    def calculate_stats(self):
        # Calculate the sum of each stat for the garden
        stat_categories = ["aesthetic_appeal", "habitat", "carbon_uptake", "waste_reduction", "health_of_garden", "innovation"]
        total_stats = {stat: 0 for stat in stat_categories}
        item_count = 0
        for item_id in self.state.values():
            try:
                # Extract the item ID from unique inventory reference
                item_pk = int(item_id.split("-")[2])  # "inventory-item-123" → 123
                item = InventoryItem.objects.get(pk=item_pk)

                # Sum stats
                for stat in stat_categories:
                    total_stats[stat] += getattr(item, stat, 0)

                item_count += 1
            except (InventoryItem.DoesNotExist, ValueError, IndexError):
                continue  # Ignore invalid or missing items

        # Compute the total for each stat NOTE - This is where you can make logic changes for how garden stats are found
        avg_stats = {stat: round(total_stats[stat], 2) if item_count else 0 for stat in stat_categories}

        # Compute the total stat score (sum of all average stats)
        total_stat_score = round(sum(avg_stats.values()), 2)

        return {"average_stats": avg_stats, "total_stats": total_stat_score}

    
    def __str__(self):
        return f"GardenState for User ID {self.user.id}"