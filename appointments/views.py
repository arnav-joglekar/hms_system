from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Availability
from .forms import AvailabilityForm
from datetime import datetime, timedelta, date as dt_date

@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        return redirect('home')
    
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            try:
                date = form.cleaned_data['date']
                start_time = form.cleaned_data['start_time']
                end_time = form.cleaned_data['end_time']
                duration = form.cleaned_data['duration']

                # Convert to datetime for calculation
                start_dt = datetime.combine(date, start_time)
                end_dt = datetime.combine(date, end_time)

                if duration == 'entire' or duration == 'custom':
                     Availability.objects.create(
                        doctor=request.user,
                        date=date,
                        start_time=start_time,
                        end_time=end_time
                    )
                else:
                    delta_minutes = int(duration)
                    current_dt = start_dt
                    while current_dt + timedelta(minutes=delta_minutes) <= end_dt:
                        slot_end = current_dt + timedelta(minutes=delta_minutes)
                        Availability.objects.create(
                            doctor=request.user,
                            date=date,
                            start_time=current_dt.time(),
                            end_time=slot_end.time()
                        )
                        current_dt = slot_end

                messages.success(request, "Availability slots added successfully.")
                return redirect('doctor_dashboard')
            except Exception as e:
                 print(f"Error adding availability: {e}")
                 messages.error(request, "Failed to add availability.")
        else:
                 messages.error(request, "Please correct the errors below.")
    else:
        form = AvailabilityForm()

    # Show future availabilities
    availabilities = Availability.objects.filter(
        doctor=request.user,
        date__gte=datetime.now().date()
    ).order_by('date', 'start_time')

    # Show upcoming appointments
    from .models import Appointment
    appointments = Appointment.objects.filter(
        availability__doctor=request.user,
        availability__date__gte=datetime.now().date()
    ).order_by('availability__date', 'availability__start_time')

    return render(request, 'appointments/doctor_dashboard.html', {
        'form': form,
        'availabilities': availabilities,
        'appointments': appointments,
        'is_google_calendar_connected': hasattr(request.user, 'google_calendar_credentials')
    })

@login_required
def patient_dashboard(request):
    if not request.user.is_patient:
        return redirect('home')
    
    # Show future available slots
    available_slots = Availability.objects.filter(
        date__gte=datetime.now().date(),
        is_booked=False
    ).order_by('date', 'start_time')

    # Show my appointments
    from .models import Appointment
    my_appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('-created_at')

    return render(request, 'appointments/patient_dashboard.html', {
        'available_slots': available_slots,
        'my_appointments': my_appointments,
        'is_google_calendar_connected': hasattr(request.user, 'google_calendar_credentials')
    })

@login_required
def book_appointment(request, slot_id):
    if not request.user.is_patient:
        return redirect('home')
    
    try:
        try:
            slot = Availability.objects.get(id=slot_id)
        except Availability.DoesNotExist:
            messages.error(request, "Slot not found.")
            return redirect('patient_dashboard')

        # Race condition check
        if slot.is_booked:
            messages.error(request, "This slot has already been booked.")
            return redirect('patient_dashboard')

        # Atomic transaction to prevent race conditions
        with transaction.atomic():
            slot = Availability.objects.select_for_update().get(id=slot_id)
            if slot.is_booked:
                 messages.error(request, "This slot has already been booked.")
                 return redirect('patient_dashboard')
            
            slot.is_booked = True
            slot.save()
            
            from .models import Appointment
            appointment = Appointment.objects.create(patient=request.user, availability=slot)
        
        # Send Confirmation Email and Create Calendar Event gracefully
        try:
            from hms_project.services import EmailService
            EmailService.send_booking_confirmation(appointment)
        except Exception as e:
             print(f"Booking confirmation email failed: {e}")
             messages.warning(request, "First attempt to contact: Email failed")

        try:
            from hms_project.google_calendar import GoogleCalendarService
            GoogleCalendarService.create_appointment_event(appointment)
        except Exception as e:
             print(f"Calendar sync event creation failed: {e}")
             messages.warning(request, "Calendar sync failed.")

        messages.success(request, "Appointment booked successfully!")
        return redirect('patient_dashboard')

    except Exception as e:
        print(f"Booking appointment error: {e}")
        messages.error(request, "Something went wrong while booking the appointment.")
        return redirect('patient_dashboard')
