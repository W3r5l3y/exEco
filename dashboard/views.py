from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import CustomUser, UserPoints
from django.db.models import F


def root_redirect_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    else:
        return redirect("login")


@login_required(login_url="/login/")
def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")


@login_required
def get_total_leaderboard(request):
    try:
        # Get the top 10 users with the highest total points
        user_points = (
            UserPoints.objects.annotate(
                total_points=F("bingame_points")
                + F("qrscanner_points")
                + F("transport_points")
            )
            .order_by("-total_points")
            .values("user_id", "total_points")[:10]
        )

        # Get usernames for the leaderboard
        for entry in user_points:
            user = CustomUser.objects.get(id=entry["user_id"])
            entry["username"] = f"{user.first_name} {user.last_name}"
            del entry["user_id"]

        return JsonResponse(list(user_points), safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
