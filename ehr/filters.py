from random import choices
import django_filters
from django import forms
from .models import *

class StaffFilter(django_filters.FilterSet):
    last_name = django_filters.CharFilter(label='SURNAME', field_name='user__last_name', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['last_name']

class PatientFilter(django_filters.FilterSet):
    file_no = django_filters.CharFilter(label='FILE NUMBER', field_name='file_no')
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="phone",lookup_expr='iexact')                                                                                                     
    # last_name = django_filters.CharFilter(label='SURNAME', field_name='last_name', lookup_expr='icontains')

    class Meta:
        model = PatientData
        fields = ['file_no',]


class PatientReportFilter(django_filters.FilterSet):
    file_no = django_filters.CharFilter(label='FILE NUMBER', field_name='file_no')
    age_start = django_filters.NumberFilter(label="AGE R1", field_name="age", lookup_expr='gte',)
    age_end = django_filters.NumberFilter(label="AGE R2", field_name="age", lookup_expr='lte',)
    gender = django_filters.ChoiceFilter(label="GENDER",choices=PatientData.sex,empty_label="ALL",
                                         widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none w-1/3 sm:w-fit text-indigo-800 rounded shadow-sm shadow-indigo-600 border-indigo-600 border'}))
    marital_status = django_filters.ChoiceFilter(label="MARITAL STATUS",choices=PatientData.m_status, 
                                                 widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none w-1/3 sm:w-fit text-indigo-800 rounded shadow-sm shadow-indigo-600 border-indigo-600 border'}))
    religion = django_filters.ChoiceFilter(label="RELIGION",choices=PatientData.faith,
                                           widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none w-1/3 sm:w-fit text-indigo-800 rounded shadow-sm shadow-indigo-600 border-indigo-600 border'}))
    occupation = django_filters.CharFilter(label="OCCUPATION", field_name="occupation", lookup_expr='iexact')
    
    nationality = django_filters.ChoiceFilter(label="NATIONALITY",choices=PatientData.ns,
                                              widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none w-1/3 sm:w-fit text-indigo-800 rounded shadow-sm shadow-indigo-600 border-indigo-600 border'}))
    zone = django_filters.ChoiceFilter(label="GEO ZONE",choices=PatientData.geo_political_zone,
                                       widget=forms.Select(attrs={'class': 'text-center text-xs focus:outline-none w-1/3 sm:w-fit text-indigo-800 rounded shadow-sm shadow-indigo-600 border-indigo-600 border'}))
    state = django_filters.CharFilter(label="STATE", field_name="state", lookup_expr='iexact')
    lga = django_filters.CharFilter(label="LGA", field_name="lga", lookup_expr='iexact')
    address = django_filters.CharFilter(label="ADDRESS", field_name="address", lookup_expr='icontains')

    class Meta:
        model = PatientData
        fields = ['file_no','gender','marital_status','religion','occupation','nationality','zone','state','lga','address']


class PatientHandoverFilter(django_filters.FilterSet):
    dob=django_filters.CharFilter(label='DATE OF BIRTH', field_name="patient__dob",lookup_expr='exact',widget=forms.DateInput(attrs={'type': 'date'}))
    age_start = django_filters.NumberFilter(label="AGE R1", field_name="patient__age", lookup_expr='gte',)  
    age_end = django_filters.NumberFilter(label="AGE R2", field_name="patient__age", lookup_expr='lte',)
    clinic = django_filters.ChoiceFilter(label='CLINIC', field_name='clinic', lookup_expr='iexact')
    status = django_filters.ChoiceFilter(label='STATUS', choices=PatientHandover.STATUS)
    updated = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
 
    class Meta:
        model=PatientHandover
        fields=['clinic','status','updated']


class AppointmentFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(label="DATE", field_name="date", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    patient=django_filters.CharFilter(label='FILE NUMBER', field_name="patient__file_no",lookup_expr='exact')
    clinic=django_filters.CharFilter(label='CLINIC',field_name="clinic",lookup_expr='iexact')                                                                                                     
    team=django_filters.CharFilter(label='TEAM',field_name="team",lookup_expr='iexact')                                                                                                     

    class Meta:
        model = Appointment
        fields = ['patient','date','clinic','team']


class ServiceFilter(django_filters.FilterSet):
    type=django_filters.CharFilter(label='CATEGORY', field_name="type",lookup_expr='iexact')
    name=django_filters.CharFilter(label='SERVICE',field_name="name",lookup_expr='iexact')                                                                                                     
    updated = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Services
        fields = ['type','name','updated']


class PayFilter(django_filters.FilterSet):
    user=django_filters.CharFilter(label='STAFF', field_name="user__username",lookup_expr='iexact')
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    service=django_filters.CharFilter(label='SERVICE',field_name="service",lookup_expr='iexact')                                                                                                     
    # status=django_filters.BooleanFilter(label='STATUS',field_name="status")                                                                                                     
    created1 = django_filters.DateFilter(label="DATE1", field_name="created", lookup_expr='lte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    created2 = django_filters.DateFilter(label="DATE2", field_name="created", lookup_expr='gte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Paypoint
        fields = ['user','patient','service']


class RadioFilter(django_filters.FilterSet):
    updated1 = django_filters.DateFilter(label="date1", field_name="updated",lookup_expr='lte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    updated2 = django_filters.DateFilter(label="date2", field_name="updated",lookup_expr='gte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    patient_no=django_filters.NumberFilter(label='pn', field_name="patient__file_no",lookup_expr='exact')
    test=django_filters.CharFilter(label='test',field_name="test__name",lookup_expr='iexact')                                                                                                     

    class Meta:
        model=RadiologyResult
        fields=['patient_no','test']

class AdmissionFilter(django_filters.FilterSet):
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    ward=django_filters.CharFilter(label='WARD',field_name="ward",lookup_expr='iexact')                                                                                                     
    updated = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Admission
        fields = ['patient','ward','updated']


class TheatreBookingFilter(django_filters.FilterSet):
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    theatre=django_filters.CharFilter(label='THEATRE',field_name="theatre",lookup_expr='iexact')                                                                                                     
    team=django_filters.CharFilter(label='TEAM',field_name="team",lookup_expr='iexact')                                                                                                     
    date = django_filters.DateFilter(label="DATE", field_name="date", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = TheatreBooking
        fields = ['patient','theatre','team','date']


class OperationNotesFilter(django_filters.FilterSet):
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    type_of_anaesthesia=django_filters.CharFilter(label='ANAESTHESIA',field_name="type_of_anaesthesia",lookup_expr='iexact')                                                                                                     
    findings=django_filters.CharFilter(label='FINDINGS',field_name="findings",lookup_expr='iexact')                                                                                                     
    date = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = OperationNotes
        fields = ['patient','type_of_anaesthesia','findings','date']

class OperatingTheatreFilter(django_filters.FilterSet):
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    date = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = OperatingTheatre
        fields = ['patient','date']


class TheatreOperationRecordFilter(django_filters.FilterSet):
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    date = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = TheatreOperationRecord
        fields = ['patient','date']