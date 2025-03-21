from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, ChangeProfileForm, ChangePasswordForm
from .models import CustomUser, UserPoints, UserCoins
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from transport.models import StravaToken, LoggedActivity
from datetime import date
from .utils import create_empty_garden_image, generate_profile_picture
from django.conf import settings
import pygame
import os
from datetime import datetime
import tempfile
import zipfile
from forum.models import Post


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
            date_now = datetime.now().strftime('%d_%m_%Y')
            
            # Setup the GDPR text
            gdpr_text = f"------------------------------------------------------------\n     EXECO\n------------------------------------------------------------\n"
            gdpr_text += f"Dear {firstName}, please see the data we have stored on you:\n"
            gdpr_text += f"\n--------------------------------------------------\n     Account Section\n--------------------------------------------------\n"
            gdpr_text += f"First Name: {firstName}\n"
            gdpr_text += f"Last Name: {lastName}\n"
            gdpr_text += f"Email address: {request.user.email}\n"
            gdpr_text += f"Last login: {request.user.last_login}\n\n"
            
            # Get transport section data
            gdpr_text += f"\n--------------------------------------------------\n     Transport Section\n--------------------------------------------------\n"
            try:
                stravaToken = StravaToken.objects.get(user=request.user)
                gdpr_text += f"Athlete Id: {stravaToken.athlete_id}\n"
            except StravaToken.DoesNotExist:
                gdpr_text += "No Strava data available.\n"
            
            # Get logged activities
            loggedActivities = LoggedActivity.objects.filter(user_id=request.user.id)
            if loggedActivities.exists():
                gdpr_text += "\nLogged Activities:\n"
                for activity in loggedActivities:
                    gdpr_text += f"-- Activity {activity.activity_id}:\n"
                    gdpr_text += f"     Distance: {activity.distance}\n"
                    gdpr_text += f"     Activity Type: {activity.activity_type}\n"
            else:
                gdpr_text += "\nNo logged activities.\n"
            
            # Add forum posts
            gdpr_text += "\n--------------------------------------------------\n     Forum Section\n--------------------------------------------------\n"
            posts = Post.objects.filter(user=request.user)
            for idx, post in enumerate(posts, start=1):
                # Define the name for the image file inside the zip so it's clear which post it belongs to (post_{idx}_image{extension})
                image_extension = os.path.splitext(post.image.name)[1]
                image_name_in_zip = f"post_{idx}_image{image_extension}"
                
                gdpr_text += f"Post {idx}:\n"
                gdpr_text += f"  Description: {post.description}\n"
                gdpr_text += f"  Likes: {post.likes}\n"
                gdpr_text += f"  Created at: {post.created_at}\n"
                gdpr_text += f"  Image file name: {image_name_in_zip}\n"
                gdpr_text += f" ----- \n\n"
            
            # Create a temporary zip file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_zip:
                zip_filename = tmp_zip.name

            with zipfile.ZipFile(zip_filename, 'w') as zf:
                # Write the GDPR text file to the zip archive
                gdpr_filename = f"{firstName}_{lastName}_{date_now}.txt"
                zf.writestr(gdpr_filename, gdpr_text)
                
                # Add images from forum posts to the zip archive
                for idx, post in enumerate(posts, start=1):
                    if post.image:
                        image_path = post.image.path
                        image_extension = os.path.splitext(post.image.name)[1]
                        image_filename = f"post_{idx}_image{image_extension}"
                        zf.write(image_path, arcname=image_filename)
            
            # Prepare the zip file for download
            with open(zip_filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type="application/zip")
                response['Content-Disposition'] = f'attachment; filename={firstName}_{lastName}_{date_now}.zip'
            
            # Clean up the temporary zip file
            os.remove(zip_filename)
            
            return response
        else:
            return HttpResponseRedirect(reverse("settings") + "?error=You must be logged in to request your gdpr.")
    except Exception as e:
        print(e)
        return HttpResponseRedirect(
            reverse("settings") + "?error=Failed to request gdpr. Please contact support."
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

def tos_view(request):
    return render(request, "accounts/tos.html")

def privacy_view(request):
    return render(request, "accounts/privacy.html")