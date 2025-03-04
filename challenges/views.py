from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import UserChallenge, Challenge

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def challenges_page(request):
    return render(request, "challenges/challenges.html")

@login_required
def get_challenges(request):
    user = request.user
    
    # Get the latest assigned daily and weekly challenges
    daily_challenges = UserChallenge.objects.filter(user=user, challenge__challenge_type='daily').order_by('-assigned_at')[:3]
    weekly_challenges = UserChallenge.objects.filter(user=user, challenge__challenge_type='weekly').order_by('-assigned_at')[:5]
    
    data = {
        "daily": [{
            "id": uc.challenge.id,
            "description": uc.challenge.description,
            "points": uc.challenge.points,
            "completed": uc.completed
        } for uc in daily_challenges],
        "weekly": [{
            "id": uc.challenge.id,
            "description": uc.challenge.description,
            "points": uc.challenge.points,
            "completed": uc.completed
        } for uc in weekly_challenges]
    }
    
    return JsonResponse(data)

@csrf_exempt
@login_required
def submit_challenge(request):
    if request.method == "POST":
        user = request.user
        data = json.loads(request.body)
        challenge_id = data.get("challenge_id")
        
        try:
            user_challenge = UserChallenge.objects.get(user=user, challenge_id=challenge_id, completed=False)
            user_challenge.completed = True
            user_challenge.completed_at = timezone.now()
            user_challenge.save()
            
            return JsonResponse({"message": "Challenge submitted successfully!"})
        except UserChallenge.DoesNotExist:
            return JsonResponse({"error": "Challenge not found or already completed."}, status=400)
    
    return JsonResponse({"error": "Invalid request."}, status=400)

@login_required
def assign_new_challenges(request):
    user = request.user
    
    # Assign new daily challenges if needed
    existing_daily = UserChallenge.objects.filter(user=user, challenge__challenge_type='daily').count()
    while existing_daily < 3:
        UserChallenge.assign_new_challenge(user, 'daily')
        existing_daily += 1
    
    # Assign new weekly challenges if needed
    existing_weekly = UserChallenge.objects.filter(user=user, challenge__challenge_type='weekly').count()
    while existing_weekly < 5:
        UserChallenge.assign_new_challenge(user, 'weekly')
        existing_weekly += 1
    
    return JsonResponse({"message": "New challenges assigned."})
