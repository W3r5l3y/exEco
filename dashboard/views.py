from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def root_redirect_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    else:
        return redirect("login")


@login_required(login_url="/login/")
def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")
