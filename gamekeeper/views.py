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
from accounts.models import CustomUser, UserPoints
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

@login_required
@is_gamekeeper
def get_qr_codes(request):
    if request.method == "GET":
        # Retrieve all locations
        locations = Location.objects.all()
        qr_codes = [
            {
                "id": loc.location_code,
                "location_name": loc.location_name,
                "is_active": loc.is_active,
            }
            for loc in locations
        ]
        return JsonResponse({"qr_codes": qr_codes})
    return JsonResponse({"message": "Method not allowed."}, status=405)

@login_required
@is_gamekeeper
def enable_qr(request, qr_id):
    if request.method == "POST":
        try:
            location = Location.objects.get(location_code=qr_id)
            location.is_active = True
            location.save()
            return JsonResponse({"message": f"QR code '{location.location_name}' enabled."})
        except Location.DoesNotExist:
            return JsonResponse({"message": "QR code not found."}, status=404)
    return JsonResponse({"message": "Method not allowed."}, status=405)

@login_required
@is_gamekeeper
def disable_qr(request, qr_id):
    if request.method == "POST":
        try:
            location = Location.objects.get(location_code=qr_id)
            location.is_active = False
            location.save()
            return JsonResponse({"message": f"QR code '{location.location_name}' disabled."})
        except Location.DoesNotExist:
            return JsonResponse({"message": "QR code not found."}, status=404)
    return JsonResponse({"message": "Method not allowed."}, status=405)


"""
Transport Gamekeeper Views
"""
@login_required
@is_gamekeeper
def unlink_strava(request, user_id):
    # Tale in user_id and unlink the strava account from the user
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
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
    strava_links = list(StravaToken.objects.values_list("user_id", flat=True))
    
    if not strava_links:
        return JsonResponse({"message": "No linked Strava accounts found"})
    
    return JsonResponse({"strava_links": strava_links})

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
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Ensure the UserPoints instance exists for this user
    user_points, created = UserPoints.objects.get_or_create(user=user)

    if type == "bingame":
        success = user_points.add_points(amount, "bingame")
    elif type == "qr":
        success = user_points.add_points(amount, "qr")
    elif type == "transport":
        success = user_points.add_points(amount, "transport")
    else:
        return JsonResponse({"error": "Invalid type"}, status=400)

    if success:
        return JsonResponse({"message": "Points added"})
    else:
        return JsonResponse({"message": "Goes below zero"}, status=400)
