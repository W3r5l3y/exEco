import cv2
import numpy as np
from pyzbar.pyzbar import decode
from django.shortcuts import render
from .forms import QRCodeUploadForm
from .models import Location


def scan_qr(request):
    result = None
    location = None

    if request.method == "POST":
        # If request method is POST, get the form data
        form = QRCodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            # Convert image to numpy array
            image_array = np.asarray(bytearray(image.read()), dtype=np.uint8)
            # Decode image
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            decoded_objects = decode(img)
            if decoded_objects:
                result = decoded_objects[0].data.decode(
                    "utf-8"
                )  # Extracted string from QR code
                print(result)  # TODO remove after debugging
                try:
                    location = Location.objects.get(location_code=result)
                    location.times_visited += 1
                    location.save()
                    print(location)  # TODO remove after debugging
                except Location.DoesNotExist:
                    result = "Location not found for code: " + result

    else:
        # If request method is not POST, create a new form
        form = QRCodeUploadForm()

    # Render the template with the form and result
    return render(
        request,
        "qrscanner/scan_qr.html",
        {"form": form, "result": result, "location": location},
    )
