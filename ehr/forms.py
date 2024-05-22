from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import *

class CustomUserCreationForm(UserCreationForm):
    middle_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name',
                  'last_name', 'password1', 'password2']
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class ProfileForm(forms.ModelForm):
    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if self.instance.dob and dob != self.instance.dob:
            raise forms.ValidationError('this action is forbidden, {} is the default'.format(
                self.instance.dob.strftime("%m-%d-%Y")))
        return dob

    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'})
        }
        exclude = ['user', 'created', 'updated']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})

class PatientForm(forms.ModelForm):
    clinic = forms.ChoiceField(choices=PatientHandover.CLINIC_CHOICES, required=False)

    class Meta:
        model = PatientData
        exclude = ['file_no','user','updated']
        widgets = {
            'zone': forms.Select(attrs={'id': 'id_zone'}),
            'state': forms.Select(attrs={'id': 'id_state'}),
            'lga': forms.Select(attrs={'id': 'id_lga'}),
            'dob': forms.DateInput(attrs={'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class VisitForm(forms.ModelForm):
    clinic = forms.ChoiceField(choices=PatientHandover.CLINIC_CHOICES, required=False)

    class Meta:
        model = FollowUpVisit
        fields = ['clinic']
    
    def __init__(self, *args, **kwargs):
        super(VisitForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = [
            'body_temperature', 'pulse_rate', 'respiration_rate',
            'blood_pressure', 'blood_oxygen', 'blood_glucose',
            'weight', 'height','handover_room',
        ]
    handover_room = forms.ChoiceField(choices=[
        ('ROOM 1', 'ROOM 1'),
        ('ROOM 2', 'ROOM 2')
    ])
    def __init__(self, *args, **kwargs):
        super(VitalSignsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class FollowUpVitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = [
            'body_temperature', 'pulse_rate', 'respiration_rate',
            'blood_pressure', 'blood_oxygen', 'blood_glucose',
            'weight', 'height','handover_room',
        ]
    handover_room = forms.ChoiceField(choices=[
        ('ROOM 1', 'ROOM 1'),
        ('ROOM 2', 'ROOM 2')
    ])
    def __init__(self, *args, **kwargs):
        super(FollowUpVitalSignsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude=['patient','created','updated']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class ClinicalNoteForm(forms.ModelForm):
    class Meta:
        model = ClinicalNote
        fields = ('note', 'diagnosis','needs_review','appointment',)

    def __init__(self, *args, **kwargs):
        super(ClinicalNoteForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class PayForm(forms.ModelForm):
    class Meta:
        model = Paypoint
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super(PayForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class PayUpdateForm(forms.ModelForm):
    class Meta:
        model = Paypoint
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super(PayUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})
            

class DicomUploadForm(forms.ModelForm):
    class Meta:
        model = Radiology
        fields = ['dicom_file']

    def __init__(self, *args, **kwargs):
        super(DicomUploadForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})
            