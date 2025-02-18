# transport/views.py

import datetime
import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import StravaToken

def transport_view(request):
    return render(request, 'transport/transport.html')

@login_required
def strava_login(request):
    """ 
    Check if user has valid Strava credentials; otherwise, redirect to Strava OAuth.
    """
    user = request.user

    try:
        strava_token = StravaToken.objects.get(user=user)

        # If token is still valid, no need to log in again
        if strava_token.expires_at > now():
            return redirect('transport-home')  # Redirect to your app

        # If expired, refresh the token
        refresh_token = strava_token.refresh_token
        refresh_url = 'https://www.strava.com/oauth/token'
        payload = {
            'client_id': settings.STRAVA_CLIENT_ID,
            'client_secret': settings.STRAVA_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        response = requests.post(refresh_url, data=payload)
        data = response.json()

        # Update database with new tokens
        strava_token.access_token = data.get('access_token')
        strava_token.refresh_token = data.get('refresh_token')  # Strava provides a new one
        strava_token.expires_at = datetime.datetime.fromtimestamp(data.get('expires_at'))
        strava_token.save()

        return redirect('transport-home')  # Redirect after refreshing

    except StravaToken.DoesNotExist:
        # If no StravaToken exists, redirect user to Strava login
        client_id = settings.STRAVA_CLIENT_ID
        redirect_uri = settings.REDIRECT_URI
        scope = 'activity:read'
        response_type = 'code'

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
    """
    Handles the callback from Strava, exchanging the code for tokens and storing them.
    """
    # Get the code and error from the query parameters
    code = request.GET.get('code')
    error = request.GET.get('error')

    # Handle any errors
    if error:
        return render(request, 'transport/error.html', {'error': error})
    # Ensure the code is present, otherwise show an error
    if not code:
        return render(request, 'transport/error.html', {'error': 'No code returned from Strava'})

    # Exchange the code for tokens
    token_url = 'https://www.strava.com/oauth/token'
    payload = {
        'client_id': settings.STRAVA_CLIENT_ID, # Use settings to get the client ID and secret
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'code': code, # The code from the query parameters
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=payload) 
    data = response.json() # Response format is JSON: {'access_token': '...', 'refresh_token': '...', 'expires_at': '...'}

    access_token = data.get('access_token') # Access token for API requests
    refresh_token = data.get('refresh_token') # Token to refresh the access token
    expires_at = data.get('expires_at') # Unix timestamp for token expiration

    # Ensure the user is logged in (CustomUser from your accounts app)
    user = request.user

    # Create or update the user's Strava tokens
    strava_token, created = StravaToken.objects.get_or_create(user=user)
    strava_token.access_token = access_token
    strava_token.refresh_token = refresh_token
    strava_token.expires_at = datetime.datetime.fromtimestamp(expires_at)
    strava_token.save()

    return redirect('transport') # Redirect to the transport view