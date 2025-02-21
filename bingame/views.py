from django.shortcuts import render
from .models import Items, Bins
from random import sample

# Create your views here.
#Initial game view
def game_view(request):
    # Get 10 random items from the database, or less if the database doesn't have 10 items
    all_items = list(Items.objects.all())
    random_items = sample(all_items, min(10, len(all_items)))
    # Get all bins from the database
    bins = Bins.objects.all() 
    return render(request, 'bingame/bingame.html', {'items': random_items, 'bins': bins})

# Handling post for updating leaderboard
