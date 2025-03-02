import cv2
import numpy as np
from pyzbar.pyzbar import decode
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import QRCodeUploadForm
from .models import Location, ScanRecord
from accounts.models import UserPoints
from datetime import timedelta
from django.utils.timezone import now
from accounts.models import CustomUser
from django.http import JsonResponse


@login_required(login_url="/login/")
def qrscanner(request):
    # Initialise variables
    result = None
    location = None
    user_points = None
    message = ""

    if request.method == "POST":
        # If request method is POST, get the form data
        form = QRCodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            # Convert image to numpy array
            image_array = np.asarray(bytearray(image.read()), dtype=np.uint8)
            # Decode image
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            # Image preprocessing
            # Tilted images are still not being read even though very clear.
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            optimal_ret, thresh = cv2.threshold(
                blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )  # BINARY + OTSU thresholding for some reason works the best
            decoded_objects = decode(thresh)

            if not decoded_objects:
                # Try decoding the original image if thresholding fails
                decoded_objects = decode(img)

            if decoded_objects:
                result = decoded_objects[0].data.decode(
                    "utf-8"
                )  # Extracted string from QR code
                print(result)  # TODO remove after debugging
                try:
                    location = Location.objects.get(location_code=result)

                    # Check if the user has scanned this QR code before
                    scan_record, created = ScanRecord.objects.get_or_create(
                        user=request.user, location=location
                    )

                    # Calculate time since last scan
                    time_since_last_scan = now() - scan_record.last_scanned
                    # Check if cooldown has passed
                    if not created and time_since_last_scan < timedelta(
                        seconds=location.cooldown_length
                    ):
                        remaining_time = (
                            timedelta(seconds=location.cooldown_length)
                            - time_since_last_scan
                        )
                        message = f"This QR code is on cooldown. Try again in {remaining_time.seconds} seconds."
                    else:
                        # Update last scanned time
                        scan_record.last_scanned = now()
                        scan_record.save()

                        # Increment location scan count
                        location.times_visited += 1
                        location.save()

                        # Award points
                        points_awarded = location.location_value
                        user_points, created = UserPoints.objects.get_or_create(
                            user=request.user
                        )
                        user_points.add_qrscanner_points(points_awarded)
                        message = f"You earned {points_awarded} points!"
                except Location.DoesNotExist:
                    result = "Location not found for code: " + result
            else:
                message = "No QR code found in the uploaded image. Please try again."

    else:
        # If request method is not POST, create a new form
        form = QRCodeUploadForm()

    leaderboard_data = UserPoints.objects.order_by("-qrscanner_points")[:10]
    context = {
        "form": form,
        "result": result,
        "location": location,
        "user_points": user_points,
        "message": message,
        "leaderboard_data": leaderboard_data,
    }

    # Render the template with the form and result
    return render(
        request,
        "qrscanner/qrscanner.html",
        context,
    )


@login_required
def get_qrscanner_leaderboard(request):
    try:
        # Get top 10 users based on transport points
        user_points = UserPoints.objects.order_by("-qrscanner_points").values(
            "user_id", "qrscanner_points"
        )[:10]

        # Get the username of each user
        for entry in user_points:
            user = CustomUser.objects.get(id=entry["user_id"])
            entry["username"] = f"{user.first_name} {user.last_name}"
            del entry["user_id"]

        return JsonResponse(list(user_points), safe=False)  # Convert QuerySet to JSON

    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)
