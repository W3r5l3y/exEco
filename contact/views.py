from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import ContactMessage


def contact_view(request):
    return render(request, "contact/contact.html")


@require_POST
@login_required
def submit_contact_message(request):
    # Function to submit a contact message
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    # Get the message from the request
    message_text = data.get("message", "").strip()
    if not message_text:
        return JsonResponse(
            {"status": "error", "message": "No message provided"}, status=400
        )

    # Create the message
    ContactMessage.objects.create(user=request.user, message=message_text)
    return JsonResponse({"status": "success", "message": "Message submitted"})
