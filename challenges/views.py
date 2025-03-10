from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import UserChallenge, Challenge, ChallengeResetTracker
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import UserCoins 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from datetime import timedelta




@login_required(login_url="/login/")
def challenges_view(request):
    user = request.user
    tracker = ChallengeResetTracker.get_reset_tracker()
    current_time = now()

    # **Reset Daily Challenges if past midnight**
    if current_time.date() > tracker.last_daily_reset.date():
        UserChallenge.objects.filter(challenge__challenge_type="daily").delete()
        User = get_user_model()
        for user in User.objects.all():
            daily_challenges = list(Challenge.objects.filter(challenge_type="daily").order_by('?')[:3])
            for challenge in daily_challenges:
                UserChallenge.objects.create(user=user, challenge=challenge, progress=0, completed=False)

        tracker.last_daily_reset = current_time  # Update BEFORE assigning new challenges
        tracker.save()  # Save changes

    # **Reset Weekly Challenges if it's Monday and not reset this week**
    if current_time.date() >= (tracker.last_weekly_reset + timedelta(days=7)).date():
        UserChallenge.objects.filter(challenge__challenge_type="weekly").delete()
        User = get_user_model()
        for user in User.objects.all():
            weekly_challenges = list(Challenge.objects.filter(challenge_type="weekly").order_by('?')[:5])
            for challenge in weekly_challenges:
                UserChallenge.objects.create(user=user, challenge=challenge, progress=0, completed=False)

        tracker.last_weekly_reset = current_time
        tracker.save()

    # Fetch updated challenges
    daily_challenges = UserChallenge.objects.filter(user=user, challenge__challenge_type="daily")
    weekly_challenges = UserChallenge.objects.filter(user=user, challenge__challenge_type="weekly")

    return render(request, "challenges/challenges.html", {
        "daily_challenges": daily_challenges,
        "weekly_challenges": weekly_challenges
    })





@login_required
@csrf_exempt
def submit_challenge(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            challenge_id = data.get("challenge_id")

            if not request.user.is_authenticated:
                return JsonResponse({"success": False, "error": "User is not logged in."})

            user_challenge = UserChallenge.objects.get(user=request.user, challenge_id=challenge_id)

            if user_challenge.completed:
                return JsonResponse({"success": False, "message": "Challenge already completed."})

            # **Ensure progress matches the goal when completing the challenge**
            user_challenge.progress = user_challenge.challenge.goal
            user_challenge.completed = True
            user_challenge.save()

            # Reward coins
            user_coins, created = UserCoins.objects.get_or_create(user=request.user)
            user_coins.coins += user_challenge.challenge.reward
            user_coins.save()

            return JsonResponse({
                "success": True,
                "message": "Challenge completed!",
                "progress": user_challenge.progress,  # Ensuring progress is updated
                "goal": user_challenge.challenge.goal,
                "completed": user_challenge.completed,
                "new_coins": user_coins.coins
            })

        except UserChallenge.DoesNotExist:
            return JsonResponse({"success": False, "error": "Challenge not found."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request."})
