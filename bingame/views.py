from django.shortcuts import render
from .models import Items, Bins
from random import sample
#Leaderboard imports
from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import BinLeaderboardEntry
# Create your views here.
#Initial game view
@login_required
def game_view(request):
    # Get 10 random items from the database, or less if the database doesn't have 10 items
    all_items = list(Items.objects.all())
    random_items = sample(all_items, min(10, len(all_items)))
    # Get all bins from the database
    bins = Bins.objects.all() 
    return render(request, 'bingame/bingame.html', {'items': random_items, 'bins': bins})

# Handling post for updating leaderboard with received score
#@csrf_exempt
@login_required
def update_leaderboard(request):
    print(request)
    if request.method == 'POST':
        try:
            score = int(request.POST.get('user_score', 0)) #One passed in
            print(score)
            leaderboard_entry, created = BinLeaderboardEntry.objects.get_or_create(user_id=request.user.id)
            leaderboard_entry.user_score += score
            leaderboard_entry.save()
            return JsonResponse({'status': 'success', 'new_score': leaderboard_entry.user_score,})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Get the top 10 users from the leaderboard
@login_required
def get_leaderboard(request):
    try:
        leaderboard = BinLeaderboardEntry.objects.order_by("-user_score").values("user_id", "user_score")[:10]  # Get top 10 users
        return JsonResponse(list(leaderboard), safe=False)  # Convert QuerySet to JSON

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
