from django.shortcuts import render
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import GardenState
from inventory.models import Inventory

import pygame
from inventory.models import InventoryItem  # to lookup image paths
import os
from django.conf import settings

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
    
def save_garden_as_image(request):
    # Extract the state from the request body.
    try:
        data = json.loads(request.body)
        garden_state = data.get("state", {})
    except Exception as e:
        return JsonResponse({"error": f"Invalid data: {e}"}, status=400)

    # Get user_id directly from the logged-in user.
    user_id = request.user.id

    pygame.init()

    grid_size = 9
    cell_size = 64
    width = grid_size * cell_size
    height = grid_size * cell_size

    surface = pygame.Surface((width, height))
    surface.fill((255, 255, 255))

    # Build the path for the wallpaper image.
    grass_img_path = os.path.join(settings.BASE_DIR, "garden", "static", "img", "grass.png")
    try:
        # Load and scale the grass image to cover the entire surface.
        grass_img = pygame.image.load(grass_img_path)
        grass_img = pygame.transform.scale(grass_img, (width, height))
        # Blit the grass image as the background.
        surface.blit(grass_img, (0, 0))
    except Exception as e:
        print("Error loading grass image:", e)
        # Fallback to a white background if the image fails to load.
        surface.fill((255, 255, 255))


    # Build paths based on your folder structure.
    empty_img_path = os.path.join(settings.BASE_DIR, "inventory", "static", "img", "items", "empty.png")
    tree_img_path = os.path.join(settings.BASE_DIR, "garden", "static", "img", "temp-tree.png")

    def get_inventory_image_path(unique_id):
        parts = unique_id.split("-")
        if len(parts) < 3:
            return empty_img_path
        base_pk = parts[2]
        try:
            item = InventoryItem.objects.get(pk=base_pk)
            path = item.image.path
            # If the file doesn't exist at the returned path, try the known inventory static folder.
            if not os.path.exists(path):
                alt_path = os.path.join(settings.BASE_DIR, "inventory", "static", "img", "items", os.path.basename(path))
                if os.path.exists(alt_path):
                    path = alt_path
            return path
        except Exception as e:
            print(f"Error retrieving image for {unique_id}: {e}")
            return empty_img_path

    for row in range(1, grid_size + 1):
        for col in range(1, grid_size + 1):
            rect = pygame.Rect((col - 1) * cell_size, (row - 1) * cell_size, cell_size, cell_size)
            key = f"{row}-{col}"

            if row == 5 and col == 5:
                try:
                    tree_img = pygame.image.load(tree_img_path)
                    tree_img = pygame.transform.scale(tree_img, (cell_size, cell_size))
                    surface.blit(tree_img, rect)
                except Exception as e:
                    print("Error loading tree image:", e)
                continue

            if key in garden_state:
                unique_item_id = garden_state[key]
                img_path = get_inventory_image_path(unique_item_id)
            else:
                img_path = empty_img_path

            try:
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (cell_size, cell_size))
                surface.blit(img, rect)
            except Exception as e:
                print(f"Error loading image for cell {key} from {img_path}: {e}")

    file_name = f"garden_state_user{user_id}.png"
    output_path = os.path.join(settings.BASE_DIR, "garden", "static", "img", "gardens", file_name)

    try:
        pygame.image.save(surface, output_path)
        print(f"Garden image saved to {output_path}")
        response_data = {"message": f"Garden image saved to {output_path}"}
    except Exception as e:
        print("Error saving garden image:", e)
        response_data = {"error": str(e)}
    finally:
        pygame.quit()

    return JsonResponse(response_data)