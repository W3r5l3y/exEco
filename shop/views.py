from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ShopItems
from accounts.models import UserCoins
from django.http import JsonResponse
from inventory.models import Inventory
from django.conf import settings
import os
import shutil

@login_required
def shop_view(request):
    # View to display the shop items
    shop_items = ShopItems.objects.all()
    
    return render(request, 'shop/shop.html', {'shop_items': shop_items})

@login_required
def buy_item(request, item_id):
    # View to handle buying an item from the shop, returns a JSON response based on success or failure due to errors or low balance
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        shop_item = ShopItems.objects.get(itemId=item_id)
    except ShopItems.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)
    
    user_coins, created = UserCoins.objects.get_or_create(user=request.user)
    
    if user_coins.coins < shop_item.cost:
        return JsonResponse({"lowbalance": "Not enough coins"}, status=400)
    # Spend coins - deal with false response
    if not user_coins.spend_coins(shop_item.cost):
        return JsonResponse({"error": "Failed to spend coins - not enough coins in inventory"}, status=500)
    
    
    # Clean url - so it works if you pass in a file named "the image.png"
    cleaned_image = shop_item.image.name.replace(" ", "_")
    shop_item.image = cleaned_image
    
    # Copy image to inventory
    if shop_item.image:
        old_image_path = os.path.join(settings.MEDIA_ROOT, str(shop_item.image))
        new_image_dir = os.path.join(settings.MEDIA_ROOT, 'inventory/items/')
        new_image_path = os.path.join(new_image_dir, os.path.basename(shop_item.image.name))


        # Copy the file only if it doesnt exist
        if not settings.TESTING and not os.path.exists(new_image_path):
            shutil.copy(old_image_path, new_image_path)
        
        new_image_relative_path = f"inventory/items/{os.path.basename(shop_item.image.name)}"



    # Add item to user inventory
    inventory, created = Inventory.objects.get_or_create(user=request.user)
    stats = {
        "aesthetic_appeal": shop_item.aesthetic_appeal,
        "habitat": shop_item.habitat,
        "carbon_uptake": shop_item.carbon_uptake,
    }
    inventory.addItem(shop_item.name,  new_image_relative_path, item_type="regular", stats=stats)
    
    return JsonResponse({"success": "Item purchased successfully"}, status=200)