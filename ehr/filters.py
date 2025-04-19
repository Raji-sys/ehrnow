from cProfile import label
from random import choices
import django_filters
from django import forms
from .models import *

class PatientReportFilter(django_filters.FilterSet):
    file_no = django_filters.CharFilter(label='FILE NUMBER', field_name='file_no')
    age_start = django_filters.NumberFilter(label="AGE R1", field_name="age", lookup_expr='gte',)
    age_end = django_filters.NumberFilter(label="AGE R2", field_name="age", lookup_expr='lte',)
    gender = django_filters.ChoiceFilter(label="GENDER",choices=PatientData.sex,empty_label="GENDER",
                                         widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'}))
    marital_status = django_filters.ChoiceFilter(label="MARITAL STATUS",choices=PatientData.m_status,empty_label="MARITAL STATUS", 
                                                 widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'}))
    religion = django_filters.ChoiceFilter(label="RELIGION",choices=PatientData.faith,empty_label="RELIGION",
                                           widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'}))
    occupation = django_filters.CharFilter(label="OCCUPATION", field_name="occupation", lookup_expr='iexact')
    
    nationality = django_filters.ChoiceFilter(label="NATIONALITY",choices=PatientData.ns,empty_label="NATIONALITY",
                                              widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'}))
    zone = django_filters.ChoiceFilter(label="GEO ZONE",choices=PatientData.geo_political_zone,empty_label="GEO ZONE",
                                       widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'}))
    state = django_filters.CharFilter(label="STATE", field_name="state", lookup_expr='iexact')
    lga = django_filters.CharFilter(label="LGA", field_name="lga", lookup_expr='iexact')
    address = django_filters.CharFilter(label="ADDRESS", field_name="address", lookup_expr='icontains')

    class Meta:
        model = PatientData
        fields = ['file_no','gender','marital_status','religion','occupation','nationality','zone','state','lga','address']


class VisitFilter(django_filters.FilterSet):
    clinic = django_filters.ModelChoiceFilter(
        label='CLINIC',
        queryset=Clinic.objects.all(),
        widget=forms.Select(attrs={
            'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'
        })
    )
    
    team = django_filters.ModelChoiceFilter(
        queryset=Team.objects.all(),
        label='TEAM',
        widget=forms.Select(attrs={
            'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'
        }),
    )
    
    created = django_filters.DateFilter(
        label="DATE",
        field_name="created",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'
        }),
        input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y']
    )
    
    gender = django_filters.ChoiceFilter(
        field_name='patient__gender',
        choices=PatientData.sex,
        label='GENDER',
        widget=forms.Select(attrs={
            'class': 'text-center text-xs focus:outline-none w-1/3 sm:w-fit text-zinc-800 rounded shadow-sm shadow-zinc-600 border-zinc-600 border'
        })
    )
    
    age_min = django_filters.NumberFilter(
        field_name='patient__age',
        lookup_expr='gte',
        label='MIN AGE',
        widget=forms.NumberInput(attrs={
            'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'
        })
    )

    age_max = django_filters.NumberFilter(
        field_name='patient__age',
        lookup_expr='lte',
        label='MAX AGE',
        widget=forms.NumberInput(attrs={
            'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'
        })
    )
    
    # Add a filter for diagnosis
    diagnosis = django_filters.CharFilter(
        field_name='latest_diagnosis',
        lookup_expr='icontains',  # Use icontains for partial matches
        label='DIAGNOSIS',
        widget=forms.TextInput(attrs={
            'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200',
        })
    )
    seen = django_filters.BooleanFilter(
        label='SEEN',
        widget=forms.Select(choices=[('', '---------'), (True, 'Yes'), (False, 'No')],
            attrs={
                'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'
            }
        )
    )

    review = django_filters.BooleanFilter(
        label='REVIEW',
        widget=forms.Select(choices=[('', '---------'), (True, 'Yes'), (False, 'No')],
            attrs={
                'class': 'text-center text-xs focus:outline-none border border-indigo-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-indigo-200'
            }
        )
    )
    class Meta:
        model = VisitRecord
        fields = ['clinic', 'team', 'created', 'gender', 'age_min', 'age_max', 'diagnosis', 'seen', 'review']


class AppointmentFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(label="DATE", field_name="date", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    patient=django_filters.CharFilter(label='FILE NUMBER', field_name="patient__file_no",lookup_expr='exact')
    clinic=django_filters.CharFilter(label='CLINIC',field_name="clinic__name",lookup_expr='icontains')                                                                                                     
    team=django_filters.CharFilter(label='TEAM',field_name="team__name",lookup_expr='icontains')                                                                                                     

    class Meta:
        model = Appointment
        fields = ['patient','date','clinic','team']


class PayFilter(django_filters.FilterSet):
    user=django_filters.CharFilter(label='STAFF', field_name="user__username",lookup_expr='iexact')
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    service=django_filters.CharFilter(label='SERVICE',field_name="service",lookup_expr='iexact')                                                                                                  
    unit=django_filters.CharFilter(label='UNIT',field_name="unit",lookup_expr='icontains')                                                                                                  
    # status=django_filters.BooleanFilter(label='STATUS',field_name="status")                                                                                                     
    created1 = django_filters.DateFilter(label="DATE1", field_name="created", lookup_expr='lte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    created2 = django_filters.DateFilter(label="DATE2", field_name="created", lookup_expr='gte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Paypoint
        fields = ['user','patient','service']


class RadioFilter(django_filters.FilterSet):
    updated1 = django_filters.DateFilter(label="date1", field_name="updated",lookup_expr='lte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    updated2 = django_filters.DateFilter(label="date2", field_name="updated",lookup_expr='gte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    patient_no=django_filters.NumberFilter(label='pn', field_name="patient__file_no",lookup_expr='contains')
    test=django_filters.CharFilter(label='test',field_name="test__name",lookup_expr='iexact')                                                                                                     

    class Meta:
        model=RadiologyResult
        fields=['patient_no','test']

class AdmissionFilter(django_filters.FilterSet):
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    ward=django_filters.CharFilter(label='WARD',field_name="ward",lookup_expr='icontains')                                                                                                     
    updated = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Admission
        fields = ['patient','ward','updated']


class TheatreBookingFilter(django_filters.FilterSet):
    file_no=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    theatre=django_filters.CharFilter(label='THEATRE',field_name="theatre__name",lookup_expr='icontains')                                                                                                     
    team=django_filters.CharFilter(label='TEAM',field_name="team__name",lookup_expr='icontains')                                                                                                            
    date = django_filters.DateFilter(label="DATE", field_name="date", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = TheatreBooking
        fields = ['theatre','team','date']


class OperationNotesFilter(django_filters.FilterSet):
    file_no=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    type_of_anaesthesia=django_filters.CharFilter(label='ANAESTHESIA',field_name="type_of_anaesthesia",lookup_expr='icontains')                                                                                                     
    findings=django_filters.CharFilter(label='FINDINGS',field_name="findings",lookup_expr='icontains')                                                                                                     
    date = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = OperationNotes
        fields = ['file_no','type_of_anaesthesia','findings','date']

class AnaesthesiaChecklistFilter(django_filters.FilterSet):
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    date = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = AnaesthesiaChecklist
        fields = ['patient','date']


class TheatreOperationRecordFilter(django_filters.FilterSet):
    file_no=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')
    theatre=django_filters.CharFilter(label='THEATRE',field_name="theatre__name",lookup_expr='icontains')                                                                                                     
    team=django_filters.CharFilter(label='TEAM',field_name="team__name",lookup_expr='icontains')                                                                                                          
    ward=django_filters.CharFilter(label='WARD',field_name="ward__name",lookup_expr='icontains')       
    surgeon=django_filters.CharFilter(label='SURGEON',field_name="surgeon",lookup_expr='icontains')                                                                                                     
    operation=django_filters.CharFilter(label='OPERATION',field_name="operation",lookup_expr='icontains')                                                                                                     
    diagnosis=django_filters.CharFilter(label='DIAGNOSIS',field_name="diagnosis",lookup_expr='icontains')                                                                                                     
    instrument_nurse=django_filters.CharFilter(label='INSTRUMENT NURSE',field_name="instrument_nurse",lookup_expr='icontains')                                                                                                     
    circulating_nurse=django_filters.CharFilter(label='CIRCULATING NURSE',field_name="circulating_nurse",lookup_expr='icontains')                                                                                                     

    date = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = TheatreOperationRecord
        fields = ['date']


class PhysioFilter(django_filters.FilterSet):
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                              
    request_date__gte = django_filters.DateFilter(field_name='request_date', lookup_expr='gte', label='Request Date (From)', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    request_date__lte = django_filters.DateFilter(field_name='request_date', lookup_expr='lte', label='Request Date (To)', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    result_date__gte = django_filters.DateFilter(field_name='result_date', lookup_expr='gte', label='Result Date (From)', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    result_date__lte = django_filters.DateFilter(field_name='result_date', lookup_expr='lte', label='Result Date (To)', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    doctor = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    physiotherapist = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    diagnosis = django_filters.CharFilter(field_name='diagnosis', lookup_expr='icontains')
    test = django_filters.ModelChoiceFilter(queryset=PhysioTest.objects.all())

    class Meta:
        model = PhysioRequest
        fields = ['request_date__gte', 'request_date__lte', 'result_date__gte', 'result_date__lte', 'doctor', 'physiotherapist', 'diagnosis', 'test']
