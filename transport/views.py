import datetime
import requests
import json
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from accounts.decorators import is_gamekeeper
from django.utils.timezone import now
from django.http import JsonResponse
from .models import StravaToken, LoggedActivity, CumulativeStats, CustomUser
from accounts.models import UserPoints
from inventory.models import Inventory, LootboxTemplate
from challenges.models import UserChallenge


@login_required
def transport_view(request):
    # Return the main transport page
    return render(request, "transport/transport.html")


@login_required
@is_gamekeeper
def transport_error(request):
    # Return the transport error page
    return render(request, "transport/transport-error.html")


@login_required
def strava_login(request):
    user = request.user

    try:
        strava_token = StravaToken.objects.get(user=user)

        # If token is still valid, no need to log in again
        if strava_token.expires_at > now():
            return redirect("transport/transport.html")

        # If expired, refresh the token
        refresh_token = strava_token.refresh_token
        refresh_url = "https://www.strava.com/oauth/token"
        payload = {
            "client_id": settings.STRAVA_CLIENT_ID,
            "client_secret": settings.STRAVA_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(refresh_url, data=payload)
        data = response.json()

        # Update database with new tokens and expiry date
        strava_token.access_token = data.get("access_token")
        strava_token.refresh_token = data.get("refresh_token")
        strava_token.expires_at = datetime.datetime.fromtimestamp(
            data.get("expires_at")
        )
        strava_token.save()

        return redirect("transport/transport.html")

    except StravaToken.DoesNotExist:
        # If no StravaToken exists, redirect user to Strava login
        client_id = settings.STRAVA_CLIENT_ID
        redirect_uri = settings.REDIRECT_URI
        scope = "activity:read"
        response_type = "code"

        strava_auth_url = (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type={response_type}"
            f"&scope={scope}"
        )
        return redirect(strava_auth_url)


@login_required
def strava_callback(request):
    # Get the code from the query parameters
    code = request.GET.get("code")
    error = request.GET.get("error")

    # Handle any errors
    if error:
        return render(request, "transport/transport-error.html", {"error": error})
    # Ensure the code is present, otherwise show an error
    if not code:
        return render(
            request,
            "transport/transport-error.html",
            {"error": "No code returned from Strava"},
        )

    # Exchange the code for tokens
    token_url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": settings.STRAVA_CLIENT_ID,
        "client_secret": settings.STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=payload)
    data = (
        response.json()
    )  # Response format is JSON: {'access_token': '...', 'refresh_token': '...', 'expires_at': '...'}

    access_token = data.get("access_token")  # Access token for API requests
    refresh_token = data.get("refresh_token")  # Token to refresh the access token
    expires_at = data.get("expires_at")  # Unix timestamp for token expiration

    # Ensure all tokens are present
    if not access_token or not refresh_token or not expires_at:
        return render(
            request,
            "transport/transport-error.html",
            {"error": "Invalid response from Strava"},
        )

    user = request.user

    # Get the athlete ID from the Strava API
    athlete_url = "https://www.strava.com/api/v3/athlete"
    headers = {"Authorization": f"Bearer {access_token}"}
    athlete_response = requests.get(athlete_url, headers=headers)
    athlete_data = athlete_response.json()
    athlete_id = athlete_data.get("id")

    # Check if the athlete ID was successfully retrieved
    if not athlete_id:
        return render(
            request,
            "transport/transport-error.html",
            {"error": "Could not get athlete ID from Strava"},
        )

    # Check if the athlete ID is in use by another user
    if StravaToken.objects.filter(athlete_id=athlete_id).exists():
        return render(
            request,
            "transport/transport-error.html",
            {"error": "This Strava account is already linked to another user"},
        )

    # Create or update the user's Strava tokens
    strava_token, created = StravaToken.objects.get_or_create(user=user)
    strava_token.access_token = access_token
    strava_token.refresh_token = refresh_token
    strava_token.expires_at = datetime.datetime.fromtimestamp(expires_at)
    strava_token.athlete_id = athlete_id
    strava_token.save()

    return redirect("transport")


@login_required
def get_latest_activity(request):
    try:
        strava_token = StravaToken.objects.get(user=request.user)

        # Check if token is expired and refresh if needed
        if strava_token.expires_at.timestamp() < datetime.datetime.now().timestamp():
            refresh_url = "https://www.strava.com/oauth/token"
            refresh_payload = {
                "client_id": settings.STRAVA_CLIENT_ID,
                "client_secret": settings.STRAVA_CLIENT_SECRET,
                "refresh_token": strava_token.refresh_token,
                "grant_type": "refresh_token",
            }
            refresh_response = requests.post(refresh_url, data=refresh_payload).json()

            strava_token.access_token = refresh_response.get("access_token")
            strava_token.refresh_token = refresh_response.get("refresh_token")
            strava_token.expires_at = datetime.datetime.fromtimestamp(
                refresh_response.get("expires_at")
            )
            strava_token.save()

        # Get latest activity from Strava
        activities_url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {"Authorization": f"Bearer {strava_token.access_token}"}
        response = requests.get(activities_url, headers=headers)
        activities = response.json()

        if response.status_code != 200 or not activities:
            return JsonResponse({"error": "Could not fetch activities."}, status=400)

        latest_activity = activities[0]  # Get most recent activity

        return JsonResponse(
            {
                "name": latest_activity.get("name"),
                "distance": latest_activity.get("distance"),
                "moving_time": latest_activity.get("moving_time"),
                "type": latest_activity.get("type"),
            }
        )

    except StravaToken.DoesNotExist:
        return JsonResponse({"error": "No Strava account linked."}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_last_five_activities(request):
    try:
        strava_token = StravaToken.objects.get(user=request.user)

        # Check if token is expired and refresh if needed
        if strava_token.expires_at.timestamp() < datetime.datetime.now().timestamp():
            refresh_url = "https://www.strava.com/oauth/token"
            refresh_payload = {
                "client_id": settings.STRAVA_CLIENT_ID,
                "client_secret": settings.STRAVA_CLIENT_SECRET,
                "refresh_token": strava_token.refresh_token,
                "grant_type": "refresh_token",
            }
            refresh_response = requests.post(refresh_url, data=refresh_payload).json()

            strava_token.access_token = refresh_response.get("access_token")
            strava_token.refresh_token = refresh_response.get("refresh_token")
            strava_token.expires_at = datetime.datetime.fromtimestamp(
                refresh_response.get("expires_at")
            )
            strava_token.save()

        # Get latest activities from Strava
        activities_url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {"Authorization": f"Bearer {strava_token.access_token}"}
        response = requests.get(activities_url, headers=headers)
        activities = response.json()

        if response.status_code != 200 or not activities:
            return JsonResponse({"error": "Could not fetch activities."}, status=400)

        # Filter only Walk, Run, and Ride activities & exclude logged ones
        valid_activities = []
        logged_ids = LoggedActivity.objects.filter(user=request.user).values_list(
            "activity_id", flat=True
        )

        for activity in activities:
            if (
                activity["type"] in ["Run", "Ride", "Walk"]
                and activity["id"] not in logged_ids
            ):  # Exclude logged activities
                valid_activities.append(
                    {
                        "id": activity["id"],  # Strava Activity ID
                        "name": activity["name"],  # Activity name
                        "distance": activity["distance"],  # Distance in meters
                        "type": activity["type"],  # Activity type (Run, Ride, Walk)
                    }
                )
                if len(valid_activities) == 5:  # Limit to 5 activities
                    break

        return JsonResponse(valid_activities, safe=False)

    except StravaToken.DoesNotExist:
        return JsonResponse({"error": "No Strava account linked."}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def log_activity(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            activity_id = data.get("activity_id")
            distance = data.get("distance")
            activity_type = data.get("activity_type")
            option = data.get("option")

            # Check if activity is already logged
            if LoggedActivity.objects.filter(activity_id=activity_id).exists():
                return JsonResponse(
                    {"error": "This activity has already been logged."}, status=400
                )

            # Store activity
            LoggedActivity.objects.create(
                user=request.user,
                activity_id=activity_id,
                distance=distance,
                activity_type=activity_type,
                option=option,
            )

            # Update CumulativeStats
            cumulative_stats, _ = CumulativeStats.objects.get_or_create(
                user=request.user
            )
            if option == "commute".lower():
                cumulative_stats.total_commute_distance += distance
            elif option == "hobby".lower():
                cumulative_stats.total_hobby_distance += distance

            cumulative_stats.save()
            
            # Convert distance to kilometers
            distance_km = distance 

            # Update Transport Challenges
            user_challenges = UserChallenge.objects.filter(
                user=request.user, challenge__game_category="transport", completed=False
            )

            for user_challenge in user_challenges:
                user_challenge.progress += distance_km  # Add logged distance in km

                # Check if challenge is completed
                if user_challenge.progress >= user_challenge.challenge.goal:
                    user_challenge.progress = user_challenge.challenge.goal
                    user_challenge.completed = True

                user_challenge.save()

            # Update UserPoints
            score = int(distance / 100)

            user_points, _ = UserPoints.objects.get_or_create(user=request.user)

            old_points = user_points.transport_points

            user_points.add_transport_points(score)

            new_points = user_points.transport_points

            old_multiple = old_points // 20
            new_multiple = new_points // 20
            lootboxes_to_reward = new_multiple - old_multiple

            if lootboxes_to_reward > 0:
                lootbox_template = LootboxTemplate.objects.get(name="Transport Lootbox")
                # Fetch or create the user's inventory
                user_inventory, _ = Inventory.objects.get_or_create(user=request.user)
                # Add the lootboxes
                user_inventory.addLootbox(
                    lootbox_template, quantity=lootboxes_to_reward
                )

            user_points.save()

            return JsonResponse(
                {
                    "success": "Activity logged successfully!",
                    "lootboxes_to_reward": lootboxes_to_reward,
                },
                status=200,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


@login_required
def get_transport_stats(request):
    try:  # Get cumulative stats and user points
        cumulative_stats = CumulativeStats.objects.get(user=request.user)
        user_points = UserPoints.objects.get(user=request.user)

        return JsonResponse(
            {
                "total_commute_distance": cumulative_stats.total_commute_distance,
                "total_hobby_distance": cumulative_stats.total_hobby_distance,
                "points_earned": user_points.transport_points,
            }
        )
    except CumulativeStats.DoesNotExist:
        return JsonResponse({"error": "No stats available."}, status=400)

    except UserPoints.DoesNotExist:
        return JsonResponse({"error": "No leaderboard entry available."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_transport_leaderboard(request):
    try:
        # Get top 10 users based on transport points
        user_points = UserPoints.objects.order_by("-transport_points").values(
            "user_id", "transport_points"
        )[:10]

        # Get the username of each user
        for entry in user_points:
            user = CustomUser.objects.get(id=entry["user_id"])
            entry["username"] = f"{user.first_name} {user.last_name}"
            del entry["user_id"]

        return JsonResponse(list(user_points), safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
