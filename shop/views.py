from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import shopItems
# Create your views here.

#Get the shop items to frontend
@login_required
def shop_view(request):
    shop_items = shopItems.items.all()
    
    return render(request, 'shop/shop.html', {'shop_items': shop_items})

@login_required
def buy_item(request, item_id):
    pass