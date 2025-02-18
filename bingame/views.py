from django.shortcuts import render
from .models import Items, Bins

# Create your views here.
def game_view(request):
    items = Items.objects.all()  # Or use static list initially
    bins = Bins.objects.all() 
    return render(request, 'bingame/bingame.html', {'items': items, 'bins': bins})
