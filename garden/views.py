from django.shortcuts import render
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import GardenState
from inventory.models import Inventory

@login_required
def garden_view(request):
    return render(request, 'garden/garden.html')

@login_required
def load_garden(request):
    try:
        garden = GardenState.objects.filter(user=request.user).first()

        if garden:
            return JsonResponse({"state": garden.state})  # No json.loads() needed
        else:
            return JsonResponse({"state": {}}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def save_garden(request):
    if request.method == "POST":
        print("hello")
        print(request.body)
        try:
            data = json.loads(request.body)
            garden_state = data.get("state", {})

            garden, created = GardenState.objects.update_or_create(
                user=request.user, defaults={"state": garden_state}
            )
            return JsonResponse({"message": "Garden saved successfully!"}, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=400)

@login_required
def load_inventory(request):
    try:
        inventory = Inventory.objects.get(user=request.user)
        items = inventory.items.all()
        items_list = []
        for item in items:
            items_list.append({
                # Format the id so that it matches the format used in garden state.
                'id': f"inventory-item-{item.id}",
                'src': item.image.url,   # Use .url to serve the image
                'name': item.name,
                'quantity': item.quantity,
                'item_type': item.item_type,
            })
        return JsonResponse({'items': items_list})
    except Inventory.DoesNotExist:
        return JsonResponse({'items': []})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)