from django.shortcuts import render
from .models import Items, Bins
from random import sample
#Leaderboard imports
from django.http import JsonResponse
#from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import BinLeaderboard
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

# Handling post for updating leaderboard with receved score
#@csfr_exempt
@login_required
def update_leaderboard(request):
    if request.method == 'POST':
        try:
            score = int(request.POST.get('score', 0))
            user_id = request.user.id
            
            leaderboard_entry, created = BinLeaderboard.objects.get_or_create(user_id=user_id)
            leaderboard_entry.user_score += score
            leaderboard_entry.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})