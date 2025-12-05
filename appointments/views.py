from django.shortcuts import render, redirect
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

            return redirect('doctor_dashboard')
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
        'appointments': appointments
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
        'my_appointments': my_appointments
    })

@login_required
def book_appointment(request, slot_id):
    if not request.user.is_patient:
        return redirect('home')
    
    try:
        slot = Availability.objects.get(id=slot_id)
    except Availability.DoesNotExist:
        return redirect('patient_dashboard')

    # Race condition check
    if slot.is_booked:
        # TODO: Add message "Slot already booked"
        return redirect('patient_dashboard')

    # Atomic transaction to prevent race conditions
    from django.db import transaction
    with transaction.atomic():
        slot = Availability.objects.select_for_update().get(id=slot_id)
        if slot.is_booked:
             return redirect('patient_dashboard')
        
        slot.is_booked = True
        slot.save()
        
        from .models import Appointment
        appointment = Appointment.objects.create(patient=request.user, availability=slot)
    
    # Send Confirmation Email
    from hms_project.services import EmailService
    EmailService.send_booking_confirmation(appointment)

    return redirect('patient_dashboard')
