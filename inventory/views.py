from django.shortcuts import render, redirect
import random
from django.contrib import messages
from .models import Inventory, InventoryItem, LootboxContents
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.templatetags.static import static
# Create your views here.

@login_required
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
    lootbox_contents = list(LootboxContents.objects.filter(lootbox_template=lootbox.lootbox_template))
    if not lootbox_contents:
        return JsonResponse({"error": "Lootbox is empty"}, status=400)
    
    #Sort elements by probability - used for probability logic
    lootbox_contents.sort(key=lambda x: x.probability, reverse=True)
    
    #Group the probabilities i.e [0.1, 0.1, 0.3, 0.5], then matches sorted lootbox_contents list
    cumulative_probability = 0
    probability_ranges = []
    for content in lootbox_contents:
        cumulative_probability += content.probability
        probability_ranges.append([cumulative_probability, content.item])
        
    #Generate random number, pick item based on where it lands in ranges
    random_number = random.random()
    selected_item = None
    
    for probability, content in probability_ranges:
        if random_number <= probability:
            selected_item = content
            break
    
    print(f"Opening lootbox: {lootbox.name}, Selected Item: {selected_item.name}") #DEBUG
    #Add the selected item to users inventory
    inventory.addItem(
        name=selected_item.name, 
        image=selected_item.image, 
        item_type="regular",
        description=selected_item.description,
        quantity=1
        )

    #Remove the lootbox after its opened - the save() change on models means can just minus one from quantity and it will delete if it goes to 0
    lootbox.quantity -= 1
    lootbox.save()
    
    return JsonResponse({
        "success": True,
        "item_won": {
            "name": selected_item.name,
            "image": f"{selected_item.image}",
            "item_type": "regular"
        },
        "lootbox_removed": lootbox.quantity == 0  # Tell frontend if lootbox is gone
    })

@login_required
def get_inventory(request):
    inventory, created = Inventory.objects.get_or_create(user=request.user)
    items = inventory.items.all()
    return render(request, 'inventory/partials/inventory_list.html', {'items': items})