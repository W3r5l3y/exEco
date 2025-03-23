from django.shortcuts import render
from .models import Items, Bins
from random import sample

# Leaderboard imports
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import UserPoints, CustomUser
from inventory.models import Inventory, LootboxTemplate
from django.http import JsonResponse, HttpResponseBadRequest
from inventory.models import LootboxTemplate
from django.conf import settings

# Import Challenge tracking model
from challenges.models import UserChallenge


# Create your views here.
# Initial game view
@login_required
def game_view(request):
    # Get 10 random items from the database, or less if the database doesn't have 10 items
    all_items = list(Items.objects.all())
    random_items = sample(all_items, min(6, len(all_items)))
    # Get all bins from the database
    bins = Bins.objects.all()
    return render(
        request, "bingame/bingame.html", {"items": random_items, "bins": bins}
    )


# Handling post for updating leaderboard with received score
@login_required
def update_leaderboard(request):
    if request.method == "POST":
        try:
            score = int(request.POST.get("user_score", 0))
            print(score)

            user_points, created = UserPoints.objects.get_or_create(user=request.user)

            # Update Challenge Progress
            user_challenges = UserChallenge.objects.filter(
                user=request.user, challenge__game_category="bingame", completed=False
            )
            for user_challenge in user_challenges:
                user_challenge.progress += 1
                if user_challenge.progress >= user_challenge.challenge.goal:
                    user_challenge.completed = True
                user_challenge.save()

            # Lootbox logic
            old_points = user_points.bingame_points
            user_points.add_bingame_points(score)
            new_points = user_points.bingame_points

            old_multiple = old_points // 20
            new_multiple = new_points // 20
            lootboxes_to_reward = new_multiple - old_multiple
            lootbox_id = None
            # If the user has earned lootboxes, add them to the inventory
            if lootboxes_to_reward > 0:
                lootbox_template = LootboxTemplate.objects.get(name="Bingame Lootbox")
                user_inventory, _ = Inventory.objects.get_or_create(user=request.user)
                user_inventory.addLootbox(
                    lootbox_template, quantity=lootboxes_to_reward
                )
                # Return the actual lootbox id
                lootbox_id = lootbox_template.lootbox_id

            return JsonResponse(
                {
                    "status": "success",
                    "new_score": user_points.bingame_points,
                    "lootboxes_to_reward": lootboxes_to_reward,
                    "lootbox_id": lootbox_id,
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
        # Return the data as a JSON
        return JsonResponse(list(user_points), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def fetch_random_items(request):
    all_items = list(Items.objects.all())
    random_items = sample(all_items, min(6, len(all_items)))
    # Prepare the data to be sent
    item_data = []
    for item in random_items:
        item_data.append(
            {
                "id": item.item_id,
                "bin_id": item.bin_id.bin_id,
                "item_name": item.item_name,
                "item_image": request.build_absolute_uri(
                    settings.MEDIA_URL + str(item.item_image)
                ),
            }
        )
    return JsonResponse({"items": item_data})


@login_required
def get_lootbox_data(request):
    # Get the lootbox_id from the GET parameters
    lootbox_id = request.GET.get("lootbox_id")

    if not lootbox_id:
        return HttpResponseBadRequest("Missing lootbox_id parameter")

    try:
        # Retrieve the lootbox template by its primary key (lootbox_id)
        lootbox = LootboxTemplate.objects.get(lootbox_id=lootbox_id)
    except LootboxTemplate.DoesNotExist:
        return HttpResponseBadRequest("Invalid lootbox_id")

    data = {
        "lootbox_name": lootbox.name,
        "lootbox_image": lootbox.lootbox_image.url,
    }

    return JsonResponse(data)
