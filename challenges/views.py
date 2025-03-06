from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import Challenge
from django.views.decorators.csrf import csrf_exempt
import json

def challenges_view(request):
    """ Fetches active daily and weekly challenges and passes them to the template. """
    daily_challenges = Challenge.objects.filter(challenge_type=Challenge.DAILY, active=True)
    weekly_challenges = Challenge.objects.filter(challenge_type=Challenge.WEEKLY, active=True)

    return render(request, "challenges/challenges.html", {
        "daily_challenges": daily_challenges,
        "weekly_challenges": weekly_challenges,
    })

@csrf_exempt
def submit_challenge(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            challenge_id = data.get("challenge_id")

            # Get the challenge (only if active)
            challenge = Challenge.objects.get(id=challenge_id, active=True)

            # Mark the challenge as completed (deactivate it)
            challenge.active = False
            challenge.save()

            return JsonResponse({"success": True, "message": "Challenge completed!"})

        except Challenge.DoesNotExist:
            return JsonResponse({"success": False, "error": "Challenge not found."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request."})