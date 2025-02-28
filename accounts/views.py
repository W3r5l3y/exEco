from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm, ChangeProfileForm, ChangePasswordForm
from .models import CustomUser  # TODO Maybe remove later
from django.http import HttpResponseRedirect
from django.urls import reverse



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
                register_form.save()
                print("REGISTRATION SUCCESSFUL!")  ## TODO REMOVE
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
    if request.method == "POST":
        user = request.user
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
            logout(request)
        elif "delete_data" in request.POST:
            return delete_account(request)
        elif "unlink_strava" in request.POST:
            return strava_unlink(request)

    return render(request, "accounts/settings.html")



def log_out(request):
    try:
        user = request.user
        if user.is_authenticated:
            logout(request)
            return HttpResponseRedirect(reverse("login"))
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
    return render(request, "dashboard/dashboard.html")
