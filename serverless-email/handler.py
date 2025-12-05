import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(event, context):
    try:
        # Parse body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        email_type = body.get('type')
        recipient = body.get('recipient')
        data = body.get('data', {})

        if not recipient:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Recipient email is required"})
            }

        # Email Configuration
        sender_email = os.environ.get('EMAIL_USER')
        sender_password = os.environ.get('EMAIL_PASS')
        
        if not sender_email or not sender_password:
             return {
                "statusCode": 500,
                "body": json.dumps({"message": "Server misconfiguration: Missing email credentials"})
            }

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient

        if email_type == 'SIGNUP_WELCOME':
            msg['Subject'] = "Welcome to Banao Hospital!"
            text = f"Hello {data.get('username', 'User')},\n\nWelcome to Banao Hospital! We are glad to have you."
        elif email_type == 'BOOKING_CONFIRMATION':
            msg['Subject'] = "Appointment Confirmation"
            text = f"Hello {data.get('username', 'User')},\n\nYour appointment with Dr. {data.get('doctor_name')} on {data.get('date')} at {data.get('time')} has been confirmed."
        elif email_type == 'DOCTOR_APPOINTMENT_NOTIFICATION':
            msg['Subject'] = "New Appointment Notification"
            text = f"Hello Dr. {data.get('doctor_name')},\n\nYou have a new appointment with Patient {data.get('patient_name')} on {data.get('date')} at {data.get('time')}."
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": f"Unknown email type: {email_type}"})
            }

        msg.attach(MIMEText(text, 'plain'))

        # Send Email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Email sent successfully"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)})
        }
