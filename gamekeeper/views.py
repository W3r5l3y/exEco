import qrcode
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
from qrscanner.models import Location
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.decorators import is_gamekeeper
from accounts.models import CustomUser
from bingame.models import Items
from transport.models import StravaToken

@login_required
@is_gamekeeper
def gamekeeper_view(request):
    return render(request, 'gamekeeper/gamekeeper.html')

"""
QR Scanner Gamekeeper Views
"""
@login_required
@is_gamekeeper
def add_location_to_qr(request, location_code, location_name, location_fact, cooldown_length, location_value):
    # Add relevant information for a qr code to the qrscanner database, then return a Json showing the new qr code location in media
    # Add qr code location to qrscanner database
    location = Location.addLocation(
        location_code=location_code,
        location_name=location_name,
        location_fact=location_fact,
        cooldown_length=cooldown_length,
        location_value=location_value
    )
    if location == "Code already exists":
        return JsonResponse({"error": "Code already exists"}, status=400)
    
    # Generate a qr code with the location code
    # Generate the QR code
    qr = qrcode.make(location_code)

    # Define QR code filename and path
    qr_filename = f"qr_codes/{location_code}.png"
    qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)

    # Save QR code
    if not os.path.exists(os.path.dirname(qr_path)):
        os.makedirs(os.path.dirname(qr_path))

    qr.save(qr_path)

    # Return JSON response with the QR code URL
    qr_url = f"{settings.MEDIA_URL}{qr_filename}"
    return JsonResponse({"message": "Location added", "qr_code_url": qr_url})


"""
Transport Gamekeeper Views
"""
@login_required
@is_gamekeeper
def unlink_strava(request, user_id):
    # Tale in user_id and unlink the strava account from the user
    try:
        user = CustomUser.objects.get(id=user_id)    
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    
    deleted, _ = StravaToken.objects.filter(user_id=user_id).delete()
    
    if deleted:
        return JsonResponse({"message": "Strava account unlinked successfully"})
    else:
        return JsonResponse({"error": "No linked Strava account found"}, status=400)
    
def get_strava_links(request):
    # Get all the user with linked strava accounts
    pass # TODO - Implement this view

"""
Bingame Gamekeeper Views
"""
@login_required
@is_gamekeeper
def add_bingame_item(request, item_name, bin_id):
    # Add a bingame item to the bingame database - assumes that the items img url is item_name.png
    
    # Add the image to the filesystem
    # TODO - Add image upload - currently assumes that the image exists with image name as item_name.png
    item_added = Items.add_item(item_name, bin_id)
    if item_added:
        return JsonResponse({"message": "Item added"})
    else:
        return JsonResponse({"message": "Item already exists"}, status=400)
    
"""
Accounts Gamekeeper views (kinda)
"""
@login_required
@is_gamekeeper
def add_points(request, type, user_id, amount):
    # Add points to a user's minigame points
    user = CustomUser.objects.get(id=user_id)
    if type not in ["bingame", "qr", "transport"]:
        return JsonResponse({"message": "Invalid type"}, status=400)
    userPoints = user.add_points(amount, type)
    if userPoints:
        return JsonResponse({"message": "Points added"})
    else:
        return JsonResponse({"message": "Goes below zero"}, status=404)