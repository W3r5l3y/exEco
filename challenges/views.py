from django.shortcuts import render
from django.http import JsonResponse
from .models import UserChallenge, Challenge, ChallengeResetTracker
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import UserCoins 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from random import sample

@login_required(login_url="/login/")
def challenges_view(request):
    user = request.user
    tracker = ChallengeResetTracker.get_reset_tracker()
    current_time = now()

    # **Reset Daily Challenges if past midnight**
    if current_time.date() > tracker.last_daily_reset.date():
        UserChallenge.objects.filter(user=user, challenge__challenge_type="daily").delete()
        all_daily_challenges = list(Challenge.objects.filter(challenge_type="daily"))
        if len(all_daily_challenges) >= 3:
            daily_challenges = sample(all_daily_challenges, min(3, len(all_daily_challenges)))  # Pick 3 random challenges
            for challenge in daily_challenges:
                UserChallenge.objects.create(user=user, challenge=challenge, progress=0, completed=False)
        tracker.last_daily_reset = current_time
        tracker.save()

    # **Reset Weekly Challenges if it's Monday and not reset this week**
    if current_time.weekday() == 0 and current_time.date() > tracker.last_weekly_reset.date():
        UserChallenge.objects.filter(user=user, challenge__challenge_type="weekly").delete()
        all_weekly_challenges = list(Challenge.objects.filter(challenge_type="weekly"))
        if len(all_weekly_challenges) >= 5:
            weekly_challenges = sample(all_weekly_challenges, min(5, len(all_weekly_challenges)))  # Pick 5 random challenges
            for challenge in weekly_challenges:
                UserChallenge.objects.create(user=user, challenge=challenge, progress=0, completed=False)

        tracker.last_weekly_reset = current_time
        tracker.save()

    if not UserChallenge.objects.filter(user=user, challenge__challenge_type="daily").exists():
        all_daily_challenges = list(Challenge.objects.filter(challenge_type="daily"))
        if len(all_daily_challenges) >= 3:
            daily_challenges = sample(all_daily_challenges, 3)
            for challenge in daily_challenges:
                UserChallenge.objects.create(user=user, challenge=challenge, progress=0, completed=False)

    if not UserChallenge.objects.filter(user=user, challenge__challenge_type="weekly").exists():
        all_weekly_challenges = list(Challenge.objects.filter(challenge_type="weekly"))
        if len(all_weekly_challenges) >= 5:
            weekly_challenges = sample(all_weekly_challenges, 5)
            for challenge in weekly_challenges:
                UserChallenge.objects.create(user=user, challenge=challenge, progress=0, completed=False)

    if not UserChallenge.objects.filter(user=user, challenge__challenge_type="lifetime").exists():
        all_lifetime_challenges = list(Challenge.objects.filter(challenge_type="lifetime"))
        for challenge in all_lifetime_challenges:
            UserChallenge.objects.create(user=user, challenge=challenge, progress=0, completed=False)

    # Fetch user coins
    user_coins, _ = UserCoins.objects.get_or_create(user=user)

    # Fetch updated challenges
    daily_challenges = UserChallenge.objects.filter(user=user, challenge__challenge_type="daily")
    weekly_challenges = UserChallenge.objects.filter(user=user, challenge__challenge_type="weekly")
    lifetime_challenges = UserChallenge.objects.filter(user=user, challenge__challenge_type="lifetime")

    return render(request, "challenges/challenges.html", {
        "daily_challenges": daily_challenges,
        "weekly_challenges": weekly_challenges,
        "lifetime_challenges": lifetime_challenges,
        "user_coins": user_coins.coins 
    })





@login_required
def get_reset_times(request):
    tracker = ChallengeResetTracker.get_reset_tracker()
    return JsonResponse({
        "daily_reset": tracker.last_daily_reset.isoformat(),
        "weekly_reset": tracker.last_weekly_reset.isoformat()
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
