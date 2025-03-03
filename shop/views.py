from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ShopItems
from accounts.models import UserCoins
from django.http import JsonResponse
from inventory.models import Inventory
from django.conf import settings
import os
import shutil
# Create your views here.

#Get the shop items to frontend
@login_required
def shop_view(request):
    shop_items = ShopItems.objects.all()
    
    return render(request, 'shop/shop.html', {'shop_items': shop_items})

@login_required
def buy_item(request, item_id):
    #View to handle buying an item from the shop, returns a JSON response based on success or failure due to errors or low balance
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        shop_item = ShopItems.objects.get(itemId=item_id)
    except ShopItems.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)
    
    user_coins, created = UserCoins.objects.get_or_create(user=request.user)
    
    if user_coins.coins < shop_item.cost:
        return JsonResponse({"lowbalance": "Not enough coins"}, status=400)
    #Spend coins - deal with false response
    if not user_coins.spend_coins(shop_item.cost):
        return JsonResponse({"error": "Failed to spend coins - not enough coins in inventory"}, status=500)
    
    #Copy image to inventory
    if shop_item.image:
        old_image_path = os.path.join(settings.BASE_DIR, 'shop/static/img/', os.path.basename(shop_item.image.name))
        new_image_dir = os.path.join(settings.BASE_DIR, 'inventory/static/img/items/')
        new_image_path = os.path.join(new_image_dir, os.path.basename(shop_item.image.name))

        # Copy the file only if it doesnt exist
        if not os.path.exists(new_image_path):
            shutil.copy(old_image_path, new_image_path)

        new_image_relative_path = f"static/img/items/{os.path.basename(shop_item.image.name)}"
        
    #Add item to user inventory
    inventory, created = Inventory.objects.get_or_create(user=request.user)
    inventory.addItem(shop_item.name,  new_image_relative_path, item_type="regular")
    
    return JsonResponse({"success": "Item purchased succesfully"}, status=200)
    
    