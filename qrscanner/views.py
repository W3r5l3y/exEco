import cv2
import numpy as np
from pyzbar.pyzbar import decode
from django.shortcuts import render
from .forms import QRCodeUploadForm


def scan_qr(request):
    result = None
    if request.method == "POST":
        form = QRCodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            image_array = np.asarray(bytearray(image.read()), dtype=np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            decoded_objects = decode(img)
            if decoded_objects:
                result = decoded_objects[0].data.decode(
                    "utf-8"
                )  # Extract string from QR code

    else:
        form = QRCodeUploadForm()

    return render(request, "qrscanner/scan_qr.html", {"form": form, "result": result})
