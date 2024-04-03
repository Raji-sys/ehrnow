from django import forms
from .models import *


class PatientForm(forms.ModelForm):
    class Meta:
        model = PatientData
        fields = ['last_name','first_name','other_name']


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['clinic']


class PaypointForm(forms.ModelForm):
    class Meta:
        model = Paypoint
        fields = '__all__'