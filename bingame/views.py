from django.shortcuts import render
from .models import Items, Bins
from random import sample

# Leaderboard imports
from django.http import JsonResponse

# from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from accounts.models import UserPoints, CustomUser

from inventory.models import Inventory, LootboxTemplate

# Create your views here.
# Initial game view
@login_required
def game_view(request):
    # Get 10 random items from the database, or less if the database doesn't have 10 items
    all_items = list(Items.objects.all())
    random_items = sample(all_items, min(6, len(all_items)))
    # Get all bins from the database
    bins = Bins.objects.all()
    print("DEBUG 123 - ", random_items)
    return render(
        request, "bingame/bingame.html", {"items": random_items, "bins": bins}
    )


# Handling post for updating leaderboard with received score
# @csrf_exempt
@login_required
def update_leaderboard(request):
    print(request)
    if request.method == "POST":
        try:
            score = int(request.POST.get("user_score", 0))  # One passed in
            print(score)

            user_points, created = UserPoints.objects.get_or_create(user=request.user)
            
            #Loot box logic
            old_points = user_points.bingame_points
            
            user_points.add_bingame_points(score)

            new_points = user_points.bingame_points
            old_multiple = old_points // 20
            new_multiple = new_points // 20
            lootboxes_to_reward = new_multiple - old_multiple
            """
            NOTE:
            If the test for this rewards more than 20 points,
            the test will fail.
            
            This is because Lootox template wont exist in the test, as
            fixtures purposely dont run in test mode.
            """
            if lootboxes_to_reward > 0:
                lootbox_template = LootboxTemplate.objects.get(name="Bingame Lootbox")
                # Fetch or create the user's inventory
                user_inventory, _ = Inventory.objects.get_or_create(user=request.user)
                # Add the lootboxes
                user_inventory.addLootbox(lootbox_template, quantity=lootboxes_to_reward)
            
            return JsonResponse(
                {
                    "status": "success",
                    "new_score": UserPoints.bingame_points,
                    "lootboxes_to_reward": lootboxes_to_reward,
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


# Get the top 10 users from the leaderboard
@login_required
def get_bingame_leaderboard(request):
    try:
        # Get top 10 users based on bingame points
        user_points = UserPoints.objects.order_by("-bingame_points").values(
            "user_id", "bingame_points"
        )[:10]

        # Get the username of each user
        for entry in user_points:
            user = CustomUser.objects.get(id=entry["user_id"])
            entry["username"] = f"{user.first_name} {user.last_name}"
            del entry["user_id"]

        return JsonResponse(list(user_points), safe=False)  # Convert QuerySet to JSON

    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def fetch_random_items(request):
    all_items = list(Items.objects.all())
    random_items = sample(all_items, min(6, len(all_items)))
    print("DEBUG _ RANDOM ITEMS: ", random_items)
    # Prepare the data to be sent
    item_data = []
    for item in random_items:
        item_data.append(
            {
                "id": item.item_id,
                "bin_id": item.bin_id.bin_id,
                "item_name": item.item_name,
                "item_image": f"{item.item_image}",
            }
        )

    return JsonResponse({"items": item_data})
