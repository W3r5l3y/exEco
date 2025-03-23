from django.shortcuts import render
import random
from .models import Inventory, LootboxContents
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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
        
    # If wrong stat is added, it will be lootbox_id == logic
    if lootbox.lootbox_template == "Bingame Lootbox":
        selected_item.health_of_garden = 0
        selected_item.innovation = 0
        
    elif lootbox.lootbox_template == "QR Scanner Lootbox":
        selected_item.waste_reduction = 0
        selected_item.health_of_garden = 0
        
    elif lootbox.lootbox_template == "Transport Lootbox":
        selected_item.waste_reduction = 0
        selected_item.innovation = 0
        
    stats = {
        "aesthetic_appeal": selected_item.aesthetic_appeal,
        "habitat": selected_item.habitat,
        "carbon_uptake": selected_item.carbon_uptake,
        "waste_reduction": selected_item.waste_reduction,
        "health_of_garden": selected_item.health_of_garden,
        "innovation": selected_item.innovation
    }
    
    #Add the selected item to users inventory
    inventory.addItem(
        name=selected_item.name, 
        image=selected_item.image, 
        item_type="regular",
        description=selected_item.description,
        quantity=1,
        stats=stats
        )

    #Remove the lootbox after its opened - the save() change on models means can just minus one from quantity and it will delete if it goes to 0
    lootbox.quantity -= 1
    lootbox.save()
    
    return JsonResponse({
        "success": True,
        "item_won": {
            "name": selected_item.name,
            "image": request.build_absolute_uri(selected_item.image.url) if selected_item.image else None,
            "item_type": "regular"
        },
        "lootbox_removed": lootbox.quantity == 0  # Tell frontend if lootbox is gone
    })

@login_required
def get_inventory(request):
    # Get the user's inventory
    inventory, created = Inventory.objects.get_or_create(user=request.user)
    items = inventory.items.all()
    return render(request, 'inventory/partials/inventory_list.html', {'items': items})

def get_corresponding_lootbox_template(item):
    # Find the corresponding lootbox template for this item
    lootbox_contents = LootboxContents.objects.filter(item__name=item.name)
    if lootbox_contents.count() == 1:
        return lootbox_contents.first().lootbox_template
    return None

@login_required
def merge_item(request, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)
    
    inventory, _ = Inventory.objects.get_or_create(user=request.user)
    # Ensure we are dealing with a regular, mergeable item
    item = inventory.items.filter(id=item_id, item_type="regular").first()
    if not item:
        return JsonResponse({"error": "Item not found"}, status=404)
    
    if item.quantity < 5:
        return JsonResponse({"error": "Not enough items to merge"}, status=400)
    
    if not item.is_mergeable:
        return JsonResponse({"error": "This item cannot be merged"}, status=400)
    
    # Subtract 5 from the item's quantity
    item.quantity -= 5
    item.save()
    
    # Determine the corresponding lootbox template for this item
    lootbox_template = get_corresponding_lootbox_template(item)
    if not lootbox_template:
        return JsonResponse({"error": "No corresponding lootbox found for this item"}, status=400)
    
    inventory.addLootbox(lootbox_template, quantity=1)
    
    return JsonResponse({"success": True, "message": "Merge successful, lootbox added to your inventory."})