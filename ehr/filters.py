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
    last_name = django_filters.CharFilter(label='SURNAME', field_name='last_name', lookup_expr='icontains')

    class Meta:
        model = PatientData
        fields = ['file_no','last_name']


class PatientReportFilter(django_filters.FilterSet):
    file_no = django_filters.CharFilter(label='FILE NUMBER', field_name='file_no')
    dob_start = django_filters.DateFilter(label="DOB R1", field_name="dob", lookup_expr='lte',widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    dob_end = django_filters.DateFilter(label="DOB R2", field_name="dob", lookup_expr='gte',widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    gender = django_filters.CharFilter(label="GENDER", field_name="gender", lookup_expr='iexact')
    marital_status = django_filters.CharFilter(label="MARITAL STATUS", field_name="marital_status", lookup_expr='iexact')
    religion = django_filters.CharFilter(label="RELIGION", field_name="religion", lookup_expr='iexact')
    occupation = django_filters.CharFilter(label="OCCUPATION", field_name="occupation", lookup_expr='iexact')
    nationality = django_filters.CharFilter(label="NATIONALITY", field_name="nationality", lookup_expr='iexact')
    zone = django_filters.CharFilter(label="ZONE", field_name="zone", lookup_expr='iexact')
    state = django_filters.CharFilter(label="STATE", field_name="state", lookup_expr='iexact')
    lga = django_filters.CharFilter(label="LGA", field_name="lga", lookup_expr='iexact')
    address = django_filters.CharFilter(label="ADDRESS", field_name="address", lookup_expr='icontains')

    class Meta:
        model = PatientData
        fields = ['file_no','gender','marital_status','religion','occupation','nationality','zone','state','lga','address']


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
    created = django_filters.DateFilter(label="DATE", field_name="created", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Paypoint
        fields = ['user','patient','service','created']


class AdmissionFilter(django_filters.FilterSet):
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    patient_phone=django_filters.CharFilter(label='PHONE',field_name="patient__phone",lookup_expr='iexact')            
    ward=django_filters.CharFilter(label='WARD',field_name="ward",lookup_expr='iexact')                                                                                                     
    updated = django_filters.DateFilter(label="DATE", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Admission
        fields = ['patient','ward','updated']
