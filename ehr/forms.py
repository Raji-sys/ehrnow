from pyclbr import Class
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import *
from django.forms import inlineformset_factory

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
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


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
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})

class PatientForm(forms.ModelForm):
    class Meta:
        model = PatientData
        exclude = ['file_no','age','user','updated']
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
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class VisitForm(forms.ModelForm):
    class Meta:
        model = FollowUpVisit
        fields = ['clinic']
    
    def __init__(self, *args, **kwargs):
        super(VisitForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = ['body_temperature', 'pulse_rate', 'respiration_rate', 'blood_pressure', 'blood_oxygen', 'blood_glucose', 'weight', 'height', 'room']

    def __init__(self, *args, **kwargs):
        clinic = kwargs.pop('clinic', None)
        super(VitalSignsForm, self).__init__(*args, **kwargs)
        if clinic:
            self.fields['room'].queryset = Room.objects.filter(clinic=clinic)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
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
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
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
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
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
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class ClinicalNoteUpdateForm(forms.ModelForm):
    class Meta:
        model = ClinicalNote
        fields = ('needs_review',)

    def __init__(self, *args, **kwargs):
        super(ClinicalNoteUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class PayForm(forms.ModelForm):
    class Meta:
        model = Paypoint
        fields = ['payment_method','status']

    def __init__(self, *args, **kwargs):
        super(PayForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class PayUpdateForm(forms.ModelForm):
    class Meta:
        model = Paypoint
        fields = ['payment_method','status']

    def __init__(self, *args, **kwargs):
        super(PayUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})
            


class DicomUploadForm(forms.ModelForm):
    class Meta:
        model = RadiologyResult
        fields = ['dicom_file']
    def __init__(self, *args, **kwargs):
        super(DicomUploadForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})
            

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['admit','ward']

    def __init__(self, *args, **kwargs):
        super(AdmissionForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class AdmissionUpdateForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['accept','bed_number']

    def __init__(self, *args, **kwargs):
        super(AdmissionUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})
            

class WardVitalSignsForm(forms.ModelForm):
    class Meta:
        model = WardVitalSigns
        fields = [
            'body_temperature', 'pulse_rate', 'respiration_rate',
            'blood_pressure', 'blood_oxygen', 'blood_glucose',
            'weight',
        ]
    def __init__(self, *args, **kwargs):
        super(WardVitalSignsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class WardMedicationForm(forms.ModelForm):
    class Meta:
        model = WardMedication
        fields = [
            'drug', 'dose', 'comments',]
    def __init__(self, *args, **kwargs):
        super(WardMedicationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class WardNotesForm(forms.ModelForm):
    class Meta:
        model = WardClinicalNote
        fields = ['note',]
    def __init__(self, *args, **kwargs):
        super(WardNotesForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['category','item','quantity']

    def __init__(self, *args, **kwargs):
        super(BillingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class RadiologyTestForm(forms.ModelForm):
    class Meta:
        model = RadiologyResult
        fields = ['test']
    def __init__(self, *args, **kwargs):
        super(RadiologyTestForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })



class RadiologyResultForm(forms.ModelForm):
    class Meta:
        model = RadiologyResult
        fields = ['test', 'comments','cleared']
    def __init__(self, *args, **kwargs):
        super(RadiologyResultForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class TheatreBookingForm(forms.ModelForm):
    class Meta:
        model = TheatreBooking
        fields = ['theatre','team','diagnosis','operation_planned','date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(TheatreBookingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class OperationNotesForm(forms.ModelForm):
    class Meta:
        model = OperationNotes
        fields = ['operated','notes','type_of_anaesthesia','findings']

    def __init__(self, *args, **kwargs):
        super(OperationNotesForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class TheatreOperationRecordForm(forms.ModelForm):
    class Meta:
        model = TheatreOperationRecord
        exclude = ['patient','info']

    def __init__(self, *args, **kwargs):
        super(TheatreOperationRecordForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })
InstrumentCountFormSet = inlineformset_factory(
    TheatreOperationRecord, 
    InstrumentCount, 
    fields=('item', 'stage', 'count'),
    extra=15,  # 5 items * 3 stages
    can_delete=False
)


class OperatingTheatreForm(forms.ModelForm):
    class Meta:
        model = OperatingTheatre
        exclude = ['patient']
    def __init__(self, *args, **kwargs):
        super(OperatingTheatreForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

SurgicalConsumableFormSet = inlineformset_factory(
    OperatingTheatre, SurgicalConsumable, 
    fields=('item_description', 'quantity', 'cost'), 
    extra=3, can_delete=False
)
    
ImplantFormSet = inlineformset_factory(
    OperatingTheatre, Implant, 
    fields=('type_of_implant', 'quantity', 'cost'), 
    extra=3, can_delete=False
)


class AnaesthisiaChecklistForm(forms.ModelForm):
    concurrent_medical_illnesses=forms.ModelMultipleChoiceField(
        queryset=MedicalIllness.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model=AnaesthisiaChecklist
        exclude=['doctor','updated','concurrent_medical_illness','comment','patient']

    def __init__(self, *args, **kwargs):
        super(AnaesthisiaChecklistForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class PeriOPNurseForm(forms.ModelForm):
    class Meta:
        model = PeriOPNurse
        exclude=['patient','nurse','updated']

    def __init__(self, *args, **kwargs):
        super(PeriOPNurseForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class PrivateBillingForm(forms.ModelForm):
    class Meta:
        model = PrivateBilling
        fields = ['item','price']

    def __init__(self, *args, **kwargs):
        super(PrivateBillingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})
