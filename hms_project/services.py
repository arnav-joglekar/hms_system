import requests
import json
import threading
from django.conf import settings

EMAIL_SERVICE_URL = getattr(settings, 'EMAIL_SERVICE_URL', 'http://localhost:3000/dev/send-email')

class EmailService:
    @staticmethod
    def send_email(email_type, recipient, data):
        """
        Sends an email via the Serverless function.
        This is run in a separate thread to avoid blocking the main request.
        """
        def _send():
            payload = {
                "type": email_type,
                "recipient": recipient,
                "data": data
            }
            try:
                response = requests.post(EMAIL_SERVICE_URL, json=payload, timeout=5)
                response.raise_for_status()
                print(f"Email sent successfully to {recipient}")
            except Exception as e:
                print(f"Failed to send email to {recipient}: {e}")

        thread = threading.Thread(target=_send)
        thread.start()

    @staticmethod
    def send_welcome_email(user):
        EmailService.send_email(
            email_type='SIGNUP_WELCOME',
            recipient=user.email,
            data={'username': user.username}
        )

    @staticmethod
    def send_booking_confirmation(appointment):
        EmailService.send_email(
            email_type='BOOKING_CONFIRMATION',
            recipient=appointment.patient.email,
            data={
                'username': appointment.patient.username,
                'doctor_name': appointment.availability.doctor.username, # Or get full name
                'date': str(appointment.availability.date),
                'time': str(appointment.availability.start_time)
            }
        )
        
        # Notify Doctor
        if appointment.availability.doctor.email:
            EmailService.send_email(
                email_type='DOCTOR_APPOINTMENT_NOTIFICATION',
                recipient=appointment.availability.doctor.email,
                data={
                    'doctor_name': appointment.availability.doctor.username,
                    'patient_name': appointment.patient.username,
                    'date': str(appointment.availability.date),
                    'time': str(appointment.availability.start_time)
                }
            )
