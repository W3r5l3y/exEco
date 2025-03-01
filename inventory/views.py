from django.shortcuts import render, redirect
import random
from django.contrib import messages
from .models import Inventory, InventoryItem, LootboxContents
from django.contrib.auth.decorators import login_required
# Create your views here.

def inventory_view(request):
    inventory, created = Inventory.objects.get_or_create(user=request.user)
    items = inventory.items.all()
    return render(request, 'inventory/inventory.html', {'items': items})

#View to open a lootbox, takes in lootbox id, then opens the lootbox in backend (here) then returns the item, and adds it to user inventory
@login_required
def open_lootbox(request, lootbox_id):
    inventory, created = Inventory.objects.get_or_create(user=request.user)
    
    #Find the lootbox in the user's inventory
    lootbox = inventory.items.filter(id=lootbox_id, item_type="lootbox").first()
    if not lootbox:
        messages.error(request, "Lootbox not found")
        return redirect('inventory')
    
    #Get all possible items inside the lootbox
    lootbox_contents = LootboxContents.objects.filter(lootbox_template=lootbox.lootbox_template)
    if not lootbox_contents:
        messages.error(request, "Lootbox is empty")
        return redirect('inventory')
    
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
    
    messages.success(request, f"You found a {selected_item.name}")
    return redirect('inventory')