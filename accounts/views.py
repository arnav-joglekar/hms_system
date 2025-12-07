from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from .models import DoctorProfile, PatientProfile

from hms_project.services import EmailService
import os
from google_auth_oauthlib.flow import Flow
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import GoogleCalendarCredentials
from django.conf import settings

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                if user.is_doctor:
                    DoctorProfile.objects.create(user=user, specialization="General") # Default
                elif user.is_patient:
                    PatientProfile.objects.create(user=user)
                
                # Send Welcome Email
                if user.email:
                    try:
                        EmailService.send_welcome_email(user)
                    except Exception as e:
                        print(f"Failed to send welcome email: {e}")

                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('home')
            except Exception as e:
                print(f"Signup error: {e}")
                messages.error(request, "An error occurred during signup.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def google_calendar_init(request):
    try:
        # Use environment variables for client config
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/calendar.events']
        )
        
        # Indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect_uri must match exactly what was
        # registered in the Google Cloud Console.
        flow.redirect_uri = request.build_absolute_uri(reverse('google_calendar_callback'))
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        request.session['google_oauth_state'] = state
        
        return redirect(authorization_url)
    except Exception as e:
        print(f"Google Calendar Init Error: {e}")
        messages.error(request, "Failed to initialize Google Calendar connection.")
        return redirect('home')

@login_required
def google_calendar_callback(request):
    try:
        state = request.session.get('google_oauth_state')
        
        if not state:
            messages.error(request, "Invalid OAuth state. Please try again.")
            return redirect('home')
        
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/calendar.events'],
            state=state
        )
        flow.redirect_uri = request.build_absolute_uri(reverse('google_calendar_callback'))
        
        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request.get_full_path()
        flow.fetch_token(authorization_response=authorization_response)
        
        credentials = flow.credentials
        
        # Save credentials
        GoogleCalendarCredentials.objects.update_or_create(
            user=request.user,
            defaults={
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
        )
        
        messages.success(request, "Google Calendar connected successfully!")
        
        # Redirect back to appropriate dashboard
        if request.user.is_doctor:
            return redirect('doctor_dashboard')
        else:
            return redirect('patient_dashboard')
    except Exception as e:
        print(f"Google Calendar Callback Error: {e}")
        messages.error(request, "Failed to connect Google Calendar.")
        return redirect('home')
