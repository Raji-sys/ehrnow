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

class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = ['body_temperature', 'pulse_rate', 'weight']

        # widgets = {
        #     'date_obtained': forms.DateInput(attrs={'type': 'date'}),
        # }

    def __init__(self, *args, **kwargs):
        super(VitalSignsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'rounded shadow-lg hover:border-green-400 focus:border-green-800'})