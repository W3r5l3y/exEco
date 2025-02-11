from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm


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
                print(email, password)  ## TODO REMOVE
                if user is not None:
                    login(request, user)
                    return redirect("home")  # Redirect to a success page.
        elif "register" in request.POST:
            register_form = RegisterForm(request.POST)
            print("PRESSED!")  ## TODO REMOVE
            if register_form.is_valid():
                print("VALID!")  ## TODO REMOVE
                first_name = register_form.cleaned_data["first_name"]
                last_name = register_form.cleaned_data["last_name"]
                email = register_form.cleaned_data["email"]
                password = register_form.cleaned_data["password"]
                confirm_password = register_form.cleaned_data["confirm_password"]
                print(
                    first_name, last_name, email, password, confirm_password
                )  ## TODO REMOVE
                if password == confirm_password:
                    # Create user here
                    print("User created: " + email)
                return redirect(
                    "login"
                )  # Redirect to login page after successful registration
            else:
                print(register_form.errors)  # Print form errors

    return render(
        request,
        "accounts/login.html",
        {"login_form": login_form, "register_form": register_form},
    )
