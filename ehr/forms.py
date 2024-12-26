from pyclbr import Class
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import *
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

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

# class PatientForm(forms.ModelForm):
#     class Meta:
#         model = PatientData
#         exclude = ['file_no','age','user','updated']
#         widgets = {
#             'zone': forms.Select(attrs={'id': 'id_zone'}),
#             'state': forms.Select(attrs={'id': 'id_state'}),
#             'lga': forms.Select(attrs={'id': 'id_lga'}),
#             'dob': forms.DateInput(attrs={'type': 'date'})
#         }
    
#     def __init__(self, *args, **kwargs):
#         super(PatientForm, self).__init__(*args, **kwargs)
#         for field in self.fields.values():
#             # field.required=True
#             field.widget.attrs.update(
#                 {'class': 'text-center text-xs focus:outline-none border border-green-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-green-200'})
class PatientForm(forms.ModelForm):
    class Meta:
        model = PatientData
        exclude = ['file_no', 'age', 'user', 'updated']
        widgets = {
            'zone': forms.Select(attrs={'id': 'id_zone'}),
            'state': forms.Select(attrs={'id': 'id_state'}),
            'lga': forms.Select(attrs={'id': 'id_lga'}),
            'dob': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        
        # Add base styling to all fields
        for field_name, field in self.fields.items():
            # Get the model field
            model_field = self.Meta.model._meta.get_field(field_name)
            
            # Set required status based on model field
            field.required = not model_field.blank

            # Add your styling
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

            # Add empty choice only for choice fields that are optional
            if isinstance(field.widget, forms.Select) and not field.required:
                if hasattr(field, 'choices'):
                    choices = list(field.choices)
                    if choices and choices[0][0] != '':  # Only add if not already present
                        choices.insert(0, ('', '---Select---'))
                        field.choices = choices


class VisitForm(forms.ModelForm):
    class Meta:
        model = VisitRecord
        fields = ['record', 'clinic','team']
    
    def __init__(self, *args, file_no=None, **kwargs):
        super(VisitForm, self).__init__(*args, **kwargs)
        self.file_no = file_no
        # Filter records to only show 'new registration' and 'follow up'
        self.fields['record'].queryset = MedicalRecord.objects.filter(name__in=['new registration', 'follow up'])
        for field in self.fields.values():
            field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})

    def clean(self):
        cleaned_data = super().clean()
        if self.file_no:
            patient = PatientData.objects.get(file_no=self.file_no)
            existing_open_visit = VisitRecord.objects.filter(
                patient=patient,
                seen=False
            ).exists()
            if existing_open_visit:
                raise ValidationError(
                    _("This patient already has an open visit. Please close the existing visit before creating a new one."),
                    code='duplicate_visit'
                )
        return cleaned_data
    

class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = ['body_temperature', 'pulse_rate', 'respiration_rate', 'blood_pressure', 'blood_oxygen', 'blood_glucose', 'weight', 'height', 'room']

    def __init__(self, *args, **kwargs):
        clinic = kwargs.pop('clinic', None)
        super(VitalSignsForm, self).__init__(*args, **kwargs)
        if clinic:
            self.fields['room'].queryset = Room.objects.filter(clinic=clinic)

        # Additional customization of fields' widgets
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
            'weight', 'height','room',
        ]
    
    def __init__(self, *args, **kwargs):
        clinic = kwargs.pop('clinic', None)
        super(FollowUpVitalSignsForm, self).__init__(*args, **kwargs)
        if clinic:
            print(f"Filtering rooms by clinic: {clinic}")
            self.fields['room'].queryset = Room.objects.filter(clinic=clinic)
        else:
            print("No clinic passed to form.")
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })



class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude=['patient','created','updated']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time','format': '%I:%M %p' })
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
        fields = ('note', 'diagnosis','needs_review',)

    def __init__(self, *args, **kwargs):
        super(ClinicalNoteForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class ClinicalNoteUpdateForm(forms.ModelForm):
    class Meta:
        model = ClinicalNote
        fields = ('note','diagnosis','needs_review')

    def __init__(self, *args, **kwargs):
        super(ClinicalNoteUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = ["type",'name','description','price']

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
            field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class PayUpdateForm(forms.ModelForm):
    class Meta:
        model = Paypoint
        fields = ['payment_method','status']

    def __init__(self, *args, **kwargs):
        super(PayUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})
            


class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['status', 'ward', 'expected_discharge_date']
        widgets = {
            'expected_discharge_date': forms.DateInput(attrs={'type': 'date'})
        }


    def __init__(self, *args, **kwargs):
        super(AdmissionForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        ward = cleaned_data.get('ward')
        if status == 'DISCHARGE' and ward:
            raise ValidationError("Discharged patients should not be assigned a ward.")
        return cleaned_data

class AdmissionUpdateForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['status', 'bed_number'] 

    def __init__(self, *args, **kwargs):
        super(AdmissionUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        bed_number = cleaned_data.get('bed_number')
        if status == 'DISCHARGE' and bed_number:
            raise ValidationError("Discharged patients should not have a bed number assigned.")
        return cleaned_data            


class AdmissionDischargeForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['status',] 
    def __init__(self, *args, **kwargs):
        super(AdmissionDischargeForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


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


class WardShiftNotesForm(forms.ModelForm):
    class Meta:
        model = WardShiftNote
        fields = ['note',]
    def __init__(self, *args, **kwargs):
        super(WardShiftNotesForm, self).__init__(*args, **kwargs)
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
        fields = ['operated','notes','post_op_order','type_of_anaesthesia','findings']

    def __init__(self, *args, **kwargs):
        super(OperationNotesForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class AnaesthesiaChecklistForm(forms.ModelForm):
    class Meta:
        model = AnaesthesiaChecklist
        fields = ( 'transfussion', 'denctures', 'permanent', 'temporary', 'lose_teeth', 'comment', 'past_medical_history')

    def __init__(self, *args, **kwargs):
        super(AnaesthesiaChecklistForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class ConcurrentMedicalIllnessForm(forms.ModelForm):
    class Meta:
        model = ConcurrentMedicalIllness
        fields = ('illness', 'description')
    def __init__(self, *args, **kwargs):
        super(ConcurrentMedicalIllnessForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class PastSurgicalHistoryForm(forms.ModelForm):
    class Meta:
        model = PastSurgicalHistory
        fields = ('surgery', 'when', 'where', 'LA_GA', 'outcome')
        widgets = {
            'when': forms.DateInput(attrs={'type': 'date'})
        }
    def __init__(self, *args, **kwargs):
        super(PastSurgicalHistoryForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class DrugHistoryForm(forms.ModelForm):
    class Meta:
        model = DrugHistory
        fields = ('medication', 'allergies', 'is_present')
    def __init__(self, *args, **kwargs):
        super(DrugHistoryForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class SocialHistoryForm(forms.ModelForm):
    class Meta:
        model = SocialHistory
        fields = ('item', 'quantity', 'duration')
    def __init__(self, *args, **kwargs):
        super(SocialHistoryForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class LastMealForm(forms.ModelForm):
    class Meta:
        model = LastMeal
        fields = ('when', 'meal_type', 'quantity')
        widgets = {
            'when': forms.DateTimeInput(attrs={'type': 'date'})
        }
    def __init__(self, *args, **kwargs):
        super(LastMealForm, self).__init__(*args, **kwargs)
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



ConsumableUsageFormSet = inlineformset_factory(
    TheatreOperationRecord,
    ConsumableUsage,
    fields=('consumable', 'quantity'),
    extra=10,
    can_delete=False
)

ImplantUsageFormSet = inlineformset_factory(
    TheatreOperationRecord,
    ImplantUsage,
    fields=('implant', 'quantity'),
    extra=10,
    can_delete=False
)

class TheatreOperationRecordForm(forms.ModelForm):
    class Meta:
        model = TheatreOperationRecord
        exclude = ['patient', 'theatre','ward','consumables', 'implants']
        widgets = {
            'date_of_operation': forms.DateInput(attrs={'type': 'date'}),
            'tourniquet_time': forms.TimeInput(attrs={'type': 'time'}),
            'tourniquet_off_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class ArchiveForm(forms.ModelForm):
    class Meta:
        model = Archive
        fields = ['file']
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class FundWalletForm(forms.ModelForm):
    class Meta:
        model = WalletTransaction
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs.update({
            'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
        })


class PhysioRequestForm(forms.ModelForm):
    class Meta:
        model = PhysioRequest
        fields = ['test','diagnosis','remark','comment']
    def __init__(self, *args, **kwargs):
        super(PhysioRequestForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class PhysioResultForm(forms.ModelForm):
    class Meta:
        model = PhysioRequest
        fields = ['test', 'result_details','cleared']
    def __init__(self, *args, **kwargs):
        super(PhysioResultForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class RadiologyInvestigationsForm(forms.ModelForm):
    class Meta:
        model = RadiologyInvestigations
        fields = ['item']

    def __init__(self, *args, **kwargs):
        super(RadiologyInvestigationsForm, self).__init__(*args, **kwargs)

        self.fields['item'].required = True

        # Apply styling to all fields
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })