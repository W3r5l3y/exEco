from django.shortcuts import render
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import GardenState

@login_required
def garden_view(request):
    return render(request, 'garden/garden.html')

@login_required
def load_garden(request):
    try:
        garden = GardenState.objects.filter(user=request.user).first()

        if garden:
            return JsonResponse({"state": garden.state})  # No json.loads() needed
        else:
            return JsonResponse({"state": {}}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def save_garden(request):
    if request.method == "POST":
        print("hello")
        print(request.body)
        try:
            data = json.loads(request.body)
            garden_state = data.get("state", {})

            garden, created = GardenState.objects.update_or_create(
                user=request.user, defaults={"state": garden_state}
            )
            return JsonResponse({"message": "Garden saved successfully!"}, safe=False)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=400)