from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, ChangeProfileForm, ChangePasswordForm
from .models import CustomUser  # TODO Maybe remove later
from django.http import HttpResponseRedirect
from django.urls import reverse
from transport.models import StravaToken
from datetime import date

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
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    request.session["user_id"] = user.id
                    return redirect("dashboard")  # Redirect to a home page.
                else:
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
            else:
                # Extract the first error message
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

    strava_linked = StravaToken.objects.filter(expires_at__gt= date.today(), user_id= user.id).exists()
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
        return HttpResponseRedirect(
            reverse("settings") + f"?error=Failed to unlink Strava. Please contact support."
        )

    return render(request, "dashboard/dashboard.html")


def create_empty_garden_image(user):
    pygame.init()
    
    grid_size = 9
    cell_size = 64
    width = grid_size * cell_size
    height = grid_size * cell_size
    
    surface = pygame.Surface((width, height))
    
    grass_img_path = os.path.join(settings.BASE_DIR, "garden", "static", "img", "grass.png")
    try:
        grass_img = pygame.image.load(grass_img_path)
        grass_img = pygame.transform.scale(grass_img, (width, height))
        surface.blit(grass_img, (0, 0))
    except Exception as e:
        print("Error loading grass background:", e)
        surface.fill((255, 255, 255))
    
    center_rect = pygame.Rect((5 - 1) * cell_size, (5 - 1) * cell_size, cell_size, cell_size)
    tree_img_path = os.path.join(settings.BASE_DIR, "garden", "static", "img", "temp-tree.png")
    try:
        tree_img = pygame.image.load(tree_img_path)
        tree_img = pygame.transform.scale(tree_img, (cell_size, cell_size))
        surface.blit(tree_img, center_rect)
    except Exception as e:
        print("Error loading tree image:", e)
    
    file_name = f"empty_garden_user{user.id}.png"
    output_dir = os.path.join(settings.BASE_DIR, "garden", "static", "img", "gardens")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, file_name)
    
    try:
        pygame.image.save(surface, output_path)
        print(f"Empty garden image saved to {output_path}")
    except Exception as e:
        print("Error saving empty garden image:", e)
    finally:
        pygame.quit()
    
    return output_path