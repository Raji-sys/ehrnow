from django import forms
from .models import *

class PatientForm(forms.ModelForm):
    class Meta:
        model = PatientData
        fields = ['last_name','first_name','other_name']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['clinic', 'appointment_date', 'reason']