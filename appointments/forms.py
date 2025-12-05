from django import forms
from .models import Availability

class AvailabilityForm(forms.ModelForm):
    DURATION_CHOICES = [
        ('30', '30 Minutes'),
        ('60', '1 Hour'),
        ('custom', 'Custom (Use Start/End Time)'),
        ('entire', 'Entire Duration'),
    ]
    duration = forms.ChoiceField(choices=DURATION_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Availability
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
