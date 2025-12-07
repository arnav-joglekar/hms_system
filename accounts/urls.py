from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('google/calendar/init/', views.google_calendar_init, name='google_calendar_init'),
    path('google/calendar/callback/', views.google_calendar_callback, name='google_calendar_callback'),
    # path('dashboard/', views.dashboard_view, name='dashboard'),
]
