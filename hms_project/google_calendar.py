from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from accounts.models import GoogleCalendarCredentials
from datetime import datetime, timedelta

class GoogleCalendarService:
    @staticmethod
    def get_credentials(user):
        try:
            creds_model = user.google_calendar_credentials
            
            credentials = Credentials(
                token=creds_model.token,
                refresh_token=creds_model.refresh_token,
                token_uri=creds_model.token_uri,
                client_id=creds_model.client_id,
                client_secret=creds_model.client_secret,
                scopes=creds_model.scopes.split(',') if isinstance(creds_model.scopes, str) else creds_model.scopes
            )
            return credentials
        except GoogleCalendarCredentials.DoesNotExist:
            return None

    @staticmethod
    def create_appointment_event(appointment):
        """
        Creates a calendar event for both the doctor and the patient.
        """
        doctor_creds = GoogleCalendarService.get_credentials(appointment.availability.doctor)
        patient_creds = GoogleCalendarService.get_credentials(appointment.patient)

        slot = appointment.availability
        start_datetime = datetime.combine(slot.date, slot.start_time).isoformat()
        end_datetime = datetime.combine(slot.date, slot.end_time).isoformat()

        event_body = {
            'summary': f'Appointment: Dr. {appointment.availability.doctor.username} with {appointment.patient.username}',
            'description': f'Medical Appointment.\nDoctor: {appointment.availability.doctor.username}\nPatient: {appointment.patient.username}',
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'UTC', # Adjust timezone as needed or use user's timezone
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'UTC',
            },
            'attendees': [],
        }

        # If we have doctor's calendar access, create event there
        if doctor_creds:
            try:
                service = build('calendar', 'v3', credentials=doctor_creds)
                service.events().insert(calendarId='primary', body=event_body).execute()
                print(f"Event created for Doctor {appointment.availability.doctor.username}")
            except Exception as e:
                print(f"Error creating event for Doctor: {e}")

        # If we have patient's calendar access, create event there
        if patient_creds:
            try:
                service = build('calendar', 'v3', credentials=patient_creds)
                service.events().insert(calendarId='primary', body=event_body).execute()
                print(f"Event created for Patient {appointment.patient.username}")
            except Exception as e:
                print(f"Error creating event for Patient: {e}")
