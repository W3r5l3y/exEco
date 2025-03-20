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
from django.views.decorators.http import require_POST
from bingame.models import Bins
from accounts.models import CustomUser, UserPoints
from bingame.models import Items
from transport.models import StravaToken
from shop.models import ShopItems
import re
from challenges.models import Challenge
from django.shortcuts import redirect
from contact.models import ContactMessage
import json
from django.core.mail import send_mail

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

@login_required
@is_gamekeeper
def get_strava_links(request):
    # Get all the user with linked strava accounts
    strava_links = list(StravaToken.objects.values_list("user_id", flat=True))
    
    if not strava_links:
        return JsonResponse({"message": "No linked Strava accounts found"})
    
    return JsonResponse({"strava_links": strava_links})

"""
Bingame Gamekeeper Views
"""
@require_POST
@login_required
@is_gamekeeper
def add_item_to_bingame(request):
    item_name = request.POST.get("item_name")
    item_bin_id = request.POST.get("item_bin_id")
    item_picture = request.FILES.get("item_picture")
    
    if not item_name or not item_bin_id:
        return JsonResponse({"error": "Missing required fields."}, status=400)
    
    try:
        bin_obj = Bins.objects.get(bin_id=item_bin_id)
    except Bins.DoesNotExist:
        return JsonResponse({"error": "Bin not found."}, status=404)
    
    if item_picture:
        item_image_url = f"bingame/items/{item_name}.png"
    else:
        return JsonResponse({"error": "Missing item picture."}, status=400)
    
    # Check if an item with the same name already exists
    if Items.objects.filter(item_name=item_name).exists():
        return JsonResponse({"error": "Item already exists."}, status=400)
    
    # Create the new item
    item = Items.objects.create(
        item_name=item_name,
        item_image=item_image_url,
        bin_id=bin_obj
    )
    
    return JsonResponse({"item_id": item.item_id})

"""
Shop gamekeeper views     
"""

@login_required
@is_gamekeeper
def add_item_to_shop(request):
    # Add an item to the shop
    item_name = request.POST.get("item_name")
    item_price = request.POST.get("item_price")
    item_description = request.POST.get("item_description")
    item_picture = request.FILES.get("item_picture")
    if not item_name or not item_price or not item_description:
        return JsonResponse({"error": "Missing required fields."}, status=400)

    if not item_picture:
        return JsonResponse({"error": "Missing item picture."}, status=400)
    
    
    # Ensure filename is safe by replacing spaces and special characters
    safe_filename = re.sub(r"[^\w\.-]", "_", item_picture.name)

    # Save the image using Django's storage system (saves into MEDIA_ROOT/shop/)
    saved_path = default_storage.save(f"shop/{safe_filename}", item_picture)
    
    # Check if an item with the same name already exists
    if ShopItems.objects.filter(name=item_name).exists():
        return JsonResponse({"error": "Item already exists."}, status=400)

    # Create the new shop item
    item = ShopItems.objects.create(
        name=item_name,
        cost=item_price,  # Adjusted to match model field
        description=item_description,
        image=saved_path
    )

    return JsonResponse({"message": "Item added successfully", "item_id": item.itemId})



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
    
@login_required
@is_gamekeeper
def get_user_ids(request):
    users = CustomUser.objects.values("id", "email")  # Fetch both ID and email
    return JsonResponse({"user_ids": list(users)})

@require_POST
def add_challenge(request):
    """
    Handles POST from the 'Add Challenge' form.
    Creates a new Challenge object and redirects back to the Gamekeeper page.
    """
    description = request.POST.get('challenge_description')
    challenge_type = request.POST.get('challenge_type')
    game_category = request.POST.get('challenge_category')
    reward = request.POST.get('challenge_reward')
    goal = request.POST.get('challenge_goal')

    # Basic validation (you can add more checks as needed)
    if not (description and challenge_type and game_category and reward and goal):
        # If something is missing, you might return an error or handle it gracefully
        return redirect('gamekeeper')  # Or some error message

    Challenge.objects.create(
        description=description,
        challenge_type=challenge_type,
        game_category=game_category,
        reward=int(reward),
        goal=int(goal),
    )

    return redirect('gamekeeper')  # Replace with your own redirect target


"""
Contact Gamekeeper views
"""

@login_required
@is_gamekeeper
def load_contact_requests(request):
    # Fetch contact messages that have not been handled yet
    requests_qs = ContactMessage.objects.filter(complete=False)
    data = []
    for req in requests_qs:
        print("Request: ", req)
        data.append({
            'id': req.id,
            'user_email': req.user.email,
            'message': req.message,
            'created': req.created.strftime('%Y-%m-%d %H:%M')
        })

    print("Data: ", data)
    return JsonResponse({'requests': data})


@login_required
@is_gamekeeper
@require_POST
def respond_contact(request):
    try:
        data = json.loads(request.body)
        request_id = data.get('id')
        response_text = data.get('response', '').strip()
        if not request_id or not response_text:
            return JsonResponse({'status': 'error', 'message': 'Missing request ID or response.'}, status=400)
        
        # Update the database record
        contact_message = ContactMessage.objects.get(id=request_id, complete=False)
        contact_message.response = response_text
        contact_message.complete = True
        contact_message.save()

        # Create the personalized email response
        first_name = contact_message.user.first_name
        last_name = contact_message.user.last_name
        subject = "Your Contact Request"
        message = f"Hi {first_name} {last_name},\n\n{response_text}\n\nHope this helps!\nThe exEco support team"
        recipient_list = [contact_message.user.email]

        # Send the email to the user
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

        return JsonResponse({'status': 'success', 'message': 'Response sent and request marked as complete.'})
    except ContactMessage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Contact request not found or already handled.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)