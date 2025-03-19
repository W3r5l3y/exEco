from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, ChangeProfileForm, ChangePasswordForm
from .models import CustomUser, UserPoints, UserCoins
import tempfile
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from transport.models import StravaToken, LoggedActivity
from datetime import date
from .utils import create_empty_garden_image, generate_profile_picture
from django.conf import settings
import pygame
import os
from datetime import datetime

def login_register_view(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    if request.method == "POST":
        # ----- LOGIN -----
        if "login" in request.POST:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # Get the email and password from the form
                email = login_form.cleaned_data["email"]
                password = login_form.cleaned_data["password"]
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    # Check if the user has a profile picture, if not generate one
                    if not user.profile_picture:
                        profile_pic_path = generate_profile_picture(user.first_name, user.last_name, user.email, user.id)
                        user.profile_picture = profile_pic_path
                        user.save()
                    # Check if the user has a garden image by searching media/gardens/garden_state_user{user.id}.png
                    garden_image_path = os.path.join(settings.MEDIA_ROOT, "gardens", f"garden_state_user{user.id}.png")
                    if not os.path.exists(garden_image_path):
                        create_empty_garden_image(user)
                    
                    # Log the user in
                    login(request, user)
                    request.session["user_id"] = user.id
                    return redirect("dashboard")  # Redirect to a home page.
                else:
                    error_message = "Invalid login credentials"
                    return HttpResponseRedirect(reverse("login") + f"?error={error_message}&tab=login")
        # ----- REGISTER -----
        elif "register" in request.POST:
            # Create a new user with the data from the form
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                new_user = register_form.save() # Save the new user
                create_empty_garden_image(new_user) # Create an empty garden image for the user
                profile_pic_path = generate_profile_picture(new_user.first_name, new_user.last_name, new_user.email, new_user.id) # Generate a profile picture for the user
                new_user.profile_picture = profile_pic_path
                new_user.save()

                # Create a new UserPoints and UserCoins object for the new user
                UserPoints.objects.get_or_create(user=new_user)
                UserCoins.objects.get_or_create(user=new_user)

                # If the user is created successfully, log them in
                user = authenticate(request, email=new_user.email, password=register_form.cleaned_data["password"])
                if user is not None:
                    login(request, user)
                    request.session["user_id"] = user.id
                    return redirect("dashboard")  # Redirect to a home page.
                else:
                    error_message = "Invalid login credentials"
                    return HttpResponseRedirect(reverse("login") + f"?error={error_message}&tab=login")
            else:
                error_message = list(register_form.errors.values())[0][0]
                return HttpResponseRedirect(reverse("login") + f"?error={error_message}&tab=register")

    return render(request, "accounts/login.html", {"login_form": login_form, "register_form": register_form})


@login_required(login_url="/login/")
def settings_view(request):
    user = request.user
    if request.method == "POST":
        if "confirm_profile" in request.POST:
            form = ChangeProfileForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse("settings") + "?success=Profile changed successfully")

            else:
                error_message = list(form.errors.values())[0][0]
                return HttpResponseRedirect(reverse("settings") + f"?error={error_message}")
        elif "confirm_password" in request.POST:
            form = ChangePasswordForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                user = authenticate(username=user.email, password=form.cleaned_data["password"])
                if user is not None:
                    login(request, user)
                return HttpResponseRedirect(reverse("settings") + "?success=Password changed successfully")
            else:
                error_message = list(form.errors.values())[0][0]
                return HttpResponseRedirect(reverse("settings") + f"?error={error_message}")
        elif "log_out" in request.POST:
            return log_out(request)
        elif "delete_data" in request.POST:
            return delete_account(request)
        elif "unlink_strava" in request.POST:
            return strava_unlink(request)
        elif "request_gdpr" in request.POST:
            return request_gdpr(request);

    strava_linked = StravaToken.objects.filter(expires_at__gt=date.today(), user_id=user.id).exists()
    return render(request, "accounts/settings.html", {"strava_linked": strava_linked})


def log_out(request):
    try:
        if request.user.is_authenticated:
            logout(request)
            return redirect("login")
        return HttpResponseRedirect(reverse("settings") + "?error=You must be logged in to delete your account.")
    except Exception as e:
        return HttpResponseRedirect(
            reverse("settings") + f"?error=Failed to log out. Please contact support."
        )


def delete_account(request):
    try:
        if request.user.is_authenticated:
            request.user.delete()
            return HttpResponseRedirect(reverse("login"))
        else:
            return HttpResponseRedirect(reverse("settings") + "?error=You must be logged in to delete your account.")

    except Exception as e:
        return HttpResponseRedirect(
            reverse("settings") + f"?error=Failed to delete account. Please contact support."
        )

def request_gdpr(request):
    try:
        if request.user.is_authenticated:
            firstName = request.user.first_name
            lastName = request.user.last_name
            date_now = current_date = datetime.now().strftime('%d_%m_%Y')
            with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.txt') as temp_file:

                temp_file.write("Dear " + firstName + ", please see the data we have stored on you:\n")

                temp_file.write("\n\nAccount Section: " + firstName + "\n")
                temp_file.write("First Name: " + firstName + "\n")
                temp_file.write("Last Name: " + lastName + "\n")
                temp_file.write("Email address: " + request.user.email + "\n")
                temp_file.write("Last login: " + str(request.user.last_login) + "\n")

                print("DEBUG: Trying to get strava token and retrieve strava data")
                stravaToken = StravaToken.objects.get(user=request.user)
                temp_file.write("\n\nTransport Section: " + firstName + "\n")
                temp_file.write("Athlete Id: " + str(stravaToken.athlete_id) + "\n")
                temp_file.write("Logged Activity: " + str(stravaToken.athlete_id) + "\n")
                loggedActivities = LoggedActivity.objects.filter(user_id=request.user.id)
                for loggedActivity in loggedActivities:
                    temp_file.write("--Activity " + str(loggedActivity.activity_id)  + " :"+ "\n")
                    temp_file.write("  distance: " + loggedActivity.distance + "\n")
                    temp_file.write("  activity type: " + loggedActivity.activity_type + "\n")

                # Go to start of file
                temp_file.seek(0)

                # Create the file download name
                filename = firstName + "_" + lastName + "_" + date_now + ".txt"

                # Create an HTTP response with the content in the file
                response = HttpResponse(temp_file.read(), content_type='text/plain')

                # Prompt file download
                response['Content-Disposition'] = f'attachment; filename={filename}'

                return response
        else:
            return HttpResponseRedirect(reverse("settings") + "?error=You must be logged in to request your gdpr.")
    except Exception as e:
        print(e)
        return HttpResponseRedirect(
            reverse("settings") + f"?error=Failed to request gdpr. Please contact support."
        )

def strava_unlink(request):
    try:
        user = request.user
        if user.is_authenticated:
            StravaToken.objects.filter(user_id=user.id).delete()
            return HttpResponseRedirect(reverse("settings") + f"?success=Strava unlinked successfully")
        else:
            return HttpResponseRedirect(reverse("settings") + "?error=You must be logged in to delete your account.")

    except Exception as e:
        return HttpResponseRedirect(
            reverse("settings") + f"?error=Failed to unlink Strava. Please contact support."
        )

def logout_view(request):
    logout(request)
    return redirect("login")