from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.is_doctor and self.is_patient:
            raise ValidationError("User cannot be both a doctor and a patient.")
            
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr. {self.user.username}"

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    
    def __str__(self):
        return f"Patient {self.user.username}"

class GoogleCalendarCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_calendar_credentials')
    token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.URLField()
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    scopes = models.TextField()

    def __str__(self):
        return f"Google Calendar Credentials for {self.user.username}"
