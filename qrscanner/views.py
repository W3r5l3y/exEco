import cv2
import numpy as np
from pyzbar.pyzbar import decode
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import QRCodeUploadForm
from .models import Location, ScanRecord
from accounts.models import UserPoints
from datetime import timedelta
from django.utils.timezone import now
from inventory.models import Inventory, LootboxTemplate
from accounts.models import CustomUser
from django.http import JsonResponse
from django.conf import settings


@login_required(login_url="/login/")
def qrscanner(request):
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
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            # Image processing
            # Titled images are still not being read even though very clear
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
                    )
                try:
                    location = Location.objects.get(location_code=result)
                    # Check if the user has scanned this qr code before
                    scan_record, created = ScanRecord.objects.get_or_create(
                        user=request.user, location=location
                    )
                    # Calculate time since the last scan
                    time_since_last_scan = now() - scan_record.last_scanned

                    if not created and time_since_last_scan < timedelta(
                        seconds=location.cooldown_length
                    ):
                        remaining_time = timedelta(seconds=location.cooldown_length) - time_since_last_scan
                        message = f"This QR code is on cooldown. Try again in {remaining_time.seconds} seconds."
                    else:
                        scan_record.last_scanned = now()
                        scan_record.save()

                        location.times_visited += 1
                        location.save()

                        # Award points to the user
                        points_awarded = location.location_value
                        user_points, _ = UserPoints.objects.get_or_create(user=request.user)
                        old_points = user_points.qrscanner_points

                        user_points.add_qrscanner_points(location.location_value)

                        # Lootbox logic
                        new_points = user_points.qrscanner_points
                        old_multiple = old_points // 20
                        new_multiple = new_points // 20
                        lootboxes_to_reward = new_multiple - old_multiple

                        request.session['lootboxes_to_reward'] = lootboxes_to_reward  # store reward in session

                        if lootboxes_to_reward > 0:
                            if not getattr(settings, 'TESTING', False):
                                lootbox_template = LootboxTemplate.objects.get(name="QR Scanner Lootbox")
                                user_inventory, _ = Inventory.objects.get_or_create(user=request.user)
                                user_inventory.addLootbox(lootbox_template, quantity=lootboxes_to_reward)
                        message = f"You earned {points_awarded} points!"
                except Location.DoesNotExist:
                    message = f"Location not found for code: {result}"
            else:
                message = "No QR code found in the uploaded image. Please try again."

            request.session['message'] = message  # message through session
            return redirect('qrscanner')  # PRG pattern implemented

    else:
        form = QRCodeUploadForm()

    lootboxes_to_reward = request.session.pop('lootboxes_to_reward', 0)  # CHANGED: get lootboxes from session
    message = request.session.pop('message', "")  # CHANGED: get message from session

    leaderboard_data = UserPoints.objects.order_by("-qrscanner_points")[:10]

    context = {
        "form": form,
        "result": result,
        "location": location,
        "user_points": user_points,
        "message": message,
        "leaderboard_data": leaderboard_data,
        "lootboxes_to_reward": lootboxes_to_reward,
    }

    # Render the template with the form and result
    return render(request, "qrscanner/qrscanner.html", context)

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
