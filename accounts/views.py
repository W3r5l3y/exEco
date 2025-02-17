from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm
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
