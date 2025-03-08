from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import Challenge
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import UserCoins 
from django.shortcuts import render
from .models import UserChallenge
from django.contrib.auth.decorators import login_required

@login_required(login_url="/login/")
def challenges_view(request):
    user = request.user

    daily_challenges = UserChallenge.objects.filter(user=user, challenge__challenge_type="daily")
    weekly_challenges = UserChallenge.objects.filter(user=user, challenge__challenge_type="weekly")

    return render(request, "challenges/challenges.html", {
        "daily_challenges": daily_challenges,
        "weekly_challenges": weekly_challenges
    })



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UserChallenge
from accounts.models import UserCoins

@login_required
@csrf_exempt
def submit_challenge(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            challenge_id = data.get("challenge_id")

            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({"success": False, "error": "User is not logged in."})

            # Find the user's specific challenge entry
            user_challenge = UserChallenge.objects.get(user=request.user, challenge_id=challenge_id)

            # If already completed, do nothing
            if user_challenge.completed:
                return JsonResponse({"success": False, "message": "Challenge already completed."})

            # Mark the challenge as completed
            user_challenge.completed = True
            user_challenge.save()

            # Reward coins
            user_coins, created = UserCoins.objects.get_or_create(user=request.user)
            user_coins.coins += user_challenge.challenge.reward
            user_coins.save()

            return JsonResponse({
                "success": True,
                "message": "Challenge completed!",
                "new_coins": user_coins.coins
            })

        except UserChallenge.DoesNotExist:
            return JsonResponse({"success": False, "error": "Challenge not found."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request."})