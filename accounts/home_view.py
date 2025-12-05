from django.shortcuts import redirect

def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_doctor:
            return redirect('doctor_dashboard')
        elif request.user.is_patient:
            return redirect('patient_dashboard')
    return redirect('login')
