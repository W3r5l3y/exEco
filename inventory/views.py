from django.shortcuts import render, redirect
import random
from django.contrib import messages
from .models import Inventory, InventoryItem, LootboxContents
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# Create your views here.

def inventory_view(request):
    inventory, created = Inventory.objects.get_or_create(user=request.user)
    items = inventory.items.all()
    return render(request, 'inventory/inventory.html', {'items': items})

#View to open a lootbox, takes in lootbox id, then opens the lootbox in backend (here) then returns the item, and adds it to user inventory
@login_required
def open_lootbox(request, lootbox_id):
    try:
        lootbox_id = int(lootbox_id)
    except ValueError:
        return JsonResponse({"error": "Invalid lootbox ID"}, status=400)
    
    if request.method != "POST": #Only allow POST requests
        return JsonResponse({"error": "POST request required."}, status=400)
    
    inventory, created = Inventory.objects.get_or_create(user=request.user)
    
    #Find the lootbox in the user's inventory
    lootbox = inventory.items.filter(id=lootbox_id).first()
    if not lootbox:
        errorMsg = "Lootbox not found ", lootbox_id, " in user's inventory" #DEBUG
        return JsonResponse({"error": errorMsg}, status=404)
    
    #Get all possible items inside the lootbox
    lootbox_contents = LootboxContents.objects.filter(lootbox_template=lootbox.lootbox_template)
    if not lootbox_contents:
        return JsonResponse({"error": "Lootbox is empty"}, status=400)
    
    #'Open box' by choosing first item that fails based on their probability (note does mean only probability checked at front of the loop) random item
    selected_item = None
    for content in lootbox_contents:
        if random.random() < content.probability:
            selected_item = content.item
            break 
    
    #If no item was selected, choose a random (incase like 3 items all 25% individual coiuld loose so force it)
    if not selected_item:
        selected_item = random.choice(lootbox_contents).item
    
    #Add the selected item to users inventory
    inventory_item, created = InventoryItem.objects.get_or_create(inventory=inventory, name=selected_item.name, defaults={'image': selected_item.image, 'item_type': "regular", 'quantity': 1})
    if not created:
        inventory_item.quantity += 1
        inventory_item.save()
    
    #Remove the lootbox after its opened - the save() change on models means can just minus one from quantity and it will delete if it goes to 0
    lootbox.quantity -= 1
    lootbox.save()
    
    return JsonResponse({
        "success": True,
        "item_won": {
            "name": selected_item.name,
            "image": selected_item.image.url if selected_item.image else None,
            "description": selected_item.description
        },
        "lootbox_removed": lootbox.quantity == 0  # Tell frontend if lootbox is gone
    })

