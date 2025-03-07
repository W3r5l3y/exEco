import qrcode
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
from qrscanner.models import Location
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def gamekeeper_view(request):
    return render(request, 'gamekeeper/gamekeeper.html')

"""
QR Scanner Gamekeeper Views
"""
@login_required
def add_location_to_qr(request, location_code, location_name, location_fact, cooldown_length):
    # Add relevant information for a qr code to the qrscanner database, then return a Json showing the new qr code location in media
    # Add qr code location to qrscanner database
    location = Location.addLocation(
        location_code=location_code,
        location_name=location_name,
        location_fact=location_fact,
        cooldown_length=cooldown_length
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