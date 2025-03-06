from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, ChangeProfileForm, ChangePasswordForm
from .models import CustomUser  # TODO Maybe remove later
from django.http import HttpResponseRedirect
from django.urls import reverse
from transport.models import StravaToken
from datetime import date
from .utils import create_empty_garden_image, generate_profile_picture

import os
import pygame
from django.conf import settings



def login_register_view(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    if request.method == "POST":
        if "login" in request.POST:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data["email"]
                password = login_form.cleaned_data["password"]
                print("Logging in user", email, password)  ## TODO REMOVE
                user = authenticate(request, email=email, password=password)
                print("Authenticated user:", user)  ## TODO REMOVE
                if user is not None:
                    login(request, user)
                    request.session["user_id"] = user.id
                    print("LOGIN SUCCESSFUL!")  ## TODO REMOVE
                    return redirect("dashboard")  # Redirect to a home page.
                else:
                    print("Invalid login credentials")  ## TODO REMOVE
                    error_message = "Invalid login credentials"
                    return HttpResponseRedirect(
                        reverse("login") + f"?error={error_message}&tab=login"
                    )
        elif "register" in request.POST:
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                new_user = register_form.save()
                # Create an empty garden image for the new user
                create_empty_garden_image(new_user)
                # Generate a profile picture using first and last name
                profile_pic_path = generate_profile_picture(new_user.first_name, new_user.last_name, new_user.email, new_user.id)
                new_user.profile_picture = profile_pic_path
                new_user.save()
                print("REGISTRATION SUCCESSFUL! Empty garden and profile picture created.")  ## TODO REMOVE
                return HttpResponseRedirect(reverse("login") + "?tab=login")
            else:
                # Extract the first error message
                error_message = list(register_form.errors.values())[0][0]
                return HttpResponseRedirect(
                    reverse("login") + f"?error={error_message}&tab=register"
                )

    return render(
        request,
        "accounts/login.html",
        {"login_form": login_form, "register_form": register_form},
    )


@login_required(login_url="/login/")
def settings_view(request):
    user = request.user
    if request.method == "POST":

        if "confirm_profile" in request.POST:
            form = ChangeProfileForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    reverse("settings") + f"?success=Profile changed successfully"
                )
                print("PROFILE CHANGES SUCCESSFUL!")  ## TODO REMOVE
            else:
                # Extract the first error message
                error_message = list(form.errors.values())[0][0]
                return HttpResponseRedirect(
                    reverse("settings") + f"?error={error_message}"
                )
        elif "confirm_password" in request.POST:
            form = ChangePasswordForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                user = authenticate(
                    username=user.email, password=form.cleaned_data["password"]
                )
                if user is not None:
                    login(request, user)
                return HttpResponseRedirect(
                    reverse("settings") + f"?success=Password changed successfully"
                )
                print("PASSWORD CHANGES SUCCESSFUL!")  ## TODO REMOVE
            else:
                # Extract the first error message
                print(form.errors)
                error_message = list(form.errors.values())[0][0]
                return HttpResponseRedirect(
                    reverse("settings") + f"?error={error_message}"
                )
        elif "log_out" in request.POST:
            return log_out(request)
        elif "delete_data" in request.POST:
            return delete_account(request)
        elif "unlink_strava" in request.POST:
            return strava_unlink(request)

    strava_linked = StravaToken.objects.filter(expires_at__gt=date.today(), user_id=user.id).exists()
    return render(request, "accounts/settings.html", {"strava_linked": strava_linked})


def log_out(request):
    try:
        user = request.user
        if user.is_authenticated:
            logout(request)
            return redirect("login")
        else:
            return HttpResponseRedirect(reverse("settings") + "?error=You must be logged in to delete your account.")

    except Exception as e:
        print(e)
        return HttpResponseRedirect(
            reverse("settings") + f"?error=Failed to log out. Please contact support."
        )

def delete_account(request):
    try:
        user = request.user
        if user.is_authenticated:
            user.delete()
            return HttpResponseRedirect(reverse("login"))
        else:
            return HttpResponseRedirect(reverse("settings") + "?error=You must be logged in to delete your account.")

    except Exception as e:
        print(e)
        return HttpResponseRedirect(
            reverse("settings") + f"?error=Failed to delete account. Please contact support."
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
        print(e)
        return HttpResponseRedirect(
            reverse("settings") + f"?error=Failed to unlink Strava. Please contact support."
        )

    return render(request, "dashboard/dashboard.html")