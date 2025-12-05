from django.urls import path
from . import views

urlpatterns = [
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
]
