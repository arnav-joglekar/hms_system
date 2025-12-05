from django.db import models
from django.conf import settings

class Availability(models.Model):
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Availabilities"

    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time}-{self.end_time}"

class Appointment(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    availability = models.OneToOneField(Availability, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment: {self.patient} with {self.availability.doctor}"
