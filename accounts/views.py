from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm
from .models import CustomUser


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
                    print("LOGIN SUCCESSFUL!")  ## TODO REMOVE
                    return redirect("home")  # Redirect to a home page.
                else:
                    print("Invalid login credentials")  ## TODO REMOVE
        elif "register" in request.POST:
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                print("REGISTRATION SUCCESSFUL!")  ## TODO REMOVE
                return redirect(
                    "login"
                )  # Redirect to login page after successful registration
            else:
                print(
                    register_form.is_valid(), register_form.errors
                )  # Print form errors TODO REMOVE

    return render(
        request,
        "accounts/login.html",
        {"login_form": login_form, "register_form": register_form},
    )
