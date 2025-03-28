from django.shortcuts import render
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import GardenState
from inventory.models import Inventory, ItemType, InventoryItem
import pygame
import os
from django.conf import settings
from django.templatetags.static import static


@login_required
def garden_view(request):
    # Render the garden main page
    return render(request, "garden/garden.html")
    return render(request, "garden/garden.html")


@login_required
def load_garden(request):
    try:
        # Load the garden state for the current user
        garden = GardenState.objects.filter(user=request.user).first()

        if garden:
            return JsonResponse({"state": garden.state})
        else:
            return JsonResponse({"state": {}}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@login_required
def save_garden(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            garden_state = data.get("state", {})

            # Ensure garden state is a dictionary before saving
            if not isinstance(garden_state, dict):
                return JsonResponse(
                    {"error": "Invalid garden state format"}, status=400
                )

            garden, created = GardenState.objects.update_or_create(
                user=request.user, defaults={"state": garden_state}
            )

            # Calculate the stats correctly
            stats_data = garden.calculate_stats()

            return JsonResponse(
                {
                    "message": "Garden saved successfully!",
                    "average_stats": stats_data["average_stats"],
                    "total_stat": stats_data[
                        "total_stats"
                    ],  # Ensure correct key for total stats
                }
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required
def load_inventory(request):
    try:
        inventory = Inventory.objects.get(user=request.user)
        items = inventory.items.filter(item_type=ItemType.REGULAR)
        items_list = []
        for item in items:
            items_list.append(
                {
                    # Format the id so that it matches the format used in garden state.
                    "id": f"inventory-item-{item.id}",
                    "img": item.image.url,
                    "name": item.name,
                    "quantity": item.quantity,
                    "item_type": item.item_type,
                }
            )
        return JsonResponse({"items": items_list})
    except Inventory.DoesNotExist:
        return JsonResponse({"items": []})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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

    # Set up the surface for the garden image.
    grid_size = 9
    cell_size = 64
    width = grid_size * cell_size
    height = grid_size * cell_size

    surface = pygame.Surface((width, height))
    surface.fill((255, 255, 255))

    # Build the path for the wallpaper image.
    grass_img_path = os.path.join(
        settings.BASE_DIR, "garden", "static", "img", "grass.png"
    )
    try:
        # Load and scale the grass image to cover the entire surface.
        grass_img = pygame.image.load(grass_img_path)
        grass_img = pygame.transform.scale(grass_img, (width, height))
        # Blit the grass image as the background.
        surface.blit(grass_img, (0, 0))
    except Exception as e:
        # Fallback to a white background if the image fails to load.
        surface.fill((255, 255, 255))

    # Build paths based on your folder structure.
    empty_img_path = os.path.join(settings.MEDIA_ROOT, "inventory/items/empty.png")

    # Helper function to get the image path for an inventory item.
    def get_inventory_image_path(unique_id):
        parts = unique_id.split("-")
        if len(parts) < 3:
            return empty_img_path
        base_pk = parts[2]
        try:
            item = InventoryItem.objects.get(pk=base_pk)
            path = item.image.url
            # Try using static path if media path doesn't exist
            if not os.path.exists(path):
                alt_path = os.path.join(
                    settings.MEDIA_ROOT, "inventory/items/", os.path.basename(path)
                )
                if os.path.exists(alt_path):
                    path = alt_path
            return path
        except Exception as e:
            return empty_img_path

    # Iterate over garden state and draw the images on the surface.
    for row in range(1, grid_size + 1):
        for col in range(1, grid_size + 1):
            rect = pygame.Rect(
                (col - 1) * cell_size, (row - 1) * cell_size, cell_size, cell_size
            )
            key = f"{row}-{col}"

            if row == 5 and col == 5:
                try:
                    # Calculate the tree image based on score, highest possible shld be 40 : 60 *2/3 = 40
                    from garden.models import GardenState

                    garden = GardenState.objects.filter(user=request.user).first()
                    if garden:
                        stats = garden.calculate_stats()
                        total_score = stats.get("total_stats", 0)
                    else:
                        total_score = 0
                    if total_score < 8:
                        tree_level = 1
                    elif total_score < 16:
                        tree_level = 2
                    elif total_score < 24:
                        tree_level = 3
                    elif total_score < 32:
                        tree_level = 4
                    else:
                        tree_level = 5
                    tree_filename = f"tree-{tree_level}.png"
                    tree_img_path = os.path.join(
                        settings.BASE_DIR, "garden", "static", "img", tree_filename
                    )
                    tree_img = pygame.image.load(tree_img_path)
                    tree_img = pygame.transform.scale(tree_img, (cell_size, cell_size))
                    surface.blit(tree_img, rect)
                except Exception as e:
                    print("Error loading tree image:", e)
                continue

            # Get the image path for the item in the cell.
            if key in garden_state:
                unique_item_id = garden_state[key]
                img_path = get_inventory_image_path(unique_item_id)
            else:
                img_path = empty_img_path

            # Load and scale the image for the cell.
            try:
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (cell_size, cell_size))
                surface.blit(img, rect)
            except Exception as e:
                print(f"Error loading image for cell {key} from {img_path}: {e}")

    # Save the garden image to the media directory.
    file_name = f"garden_state_user{user_id}.png"
    garden_media_dir = os.path.join(settings.MEDIA_ROOT, "gardens")
    os.makedirs(garden_media_dir, exist_ok=True)

    output_path = os.path.join(garden_media_dir, file_name)
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


@login_required
def fetch_user_garden_image(request):
    # Return the URL for the garden image for the current user.
    user_id = request.user.id
    file_name = f"garden_state_user{user_id}.png"
    image_url = f"/media/gardens/{file_name}"
    return JsonResponse({"image_url": image_url})


@login_required
def get_tree_image(request):
    # Return the URL for the tree image based on the user's garden stats.
    try:
        garden = GardenState.objects.filter(user=request.user).first()
        if garden:
            stats = garden.calculate_stats()
            total_score = stats.get("total_stats", 0)
        else:
            total_score = 0
        if total_score < 8:
            tree_level = 1
        elif total_score < 16:
            tree_level = 2
        elif total_score < 24:
            tree_level = 3
        elif total_score < 32:
            tree_level = 4
        else:
            tree_level = 5
        image_path = f"/static/img/tree-{tree_level}.png"
        return JsonResponse({"tree_image": image_path})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_garden_stats(request):
    # Return the average and total stats for the user's garden.
    try:
        garden = GardenState.objects.filter(user=request.user).first()
        if garden:
            stats = garden.calculate_stats()
            return JsonResponse(
                {
                    "average_stats": stats["average_stats"],
                    "total_stat": stats["total_stats"],
                }
            )
        else:
            return JsonResponse({"average_stats": {}, "total_stat": 0})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_tree_image(request):
    try:
        garden = GardenState.objects.filter(user=request.user).first()
        if garden:
            stats = garden.calculate_stats()
            total_score = stats.get("total_stats", 0)
        else:
            total_score = 0
        if total_score < 8:
            tree_level = 1
        elif total_score < 16:
            tree_level = 2
        elif total_score < 24:
            tree_level = 3
        elif total_score < 32:
            tree_level = 4
        else:
            tree_level = 5
        image_path = f"/static/img/tree-{tree_level}.png"
        return JsonResponse({"tree_image": image_path})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_garden_stats(request):
    try:
        garden = GardenState.objects.filter(user=request.user).first()
        if garden:
            stats = garden.calculate_stats()
            return JsonResponse(
                {
                    "average_stats": stats["average_stats"],
                    "total_stat": stats["total_stats"],
                }
            )
        else:
            return JsonResponse({"average_stats": {}, "total_stat": 0})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
