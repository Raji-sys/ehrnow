import django_filters
from django import forms
from .models import *

class StaffFilter(django_filters.FilterSet):
    last_name = django_filters.CharFilter(label='SURNAME', field_name='user__last_name', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['last_name']

class PatientFilter(django_filters.FilterSet):
    file_no = django_filters.CharFilter(label='file number', field_name='file_no')

    class Meta:
        model = PatientData
        fields = ['file_no']

class AppointmentFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(label="date", field_name="date", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    patient=django_filters.CharFilter(label='file no.', field_name="patient__file_no",lookup_expr='exact')
    clinic=django_filters.CharFilter(label='clinic',field_name="clinic",lookup_expr='iexact')                                                                                                     
    team=django_filters.CharFilter(label='team',field_name="team",lookup_expr='iexact')                                                                                                     

    class Meta:
        model = Appointment
        fields = ['patient','date','clinic','team']


class ServiceFilter(django_filters.FilterSet):
    type=django_filters.CharFilter(label='CATEGORY', field_name="type",lookup_expr='iexact')
    name=django_filters.CharFilter(label='SERVICE',field_name="name",lookup_expr='iexact')                                                                                                     
    updated = django_filters.DateFilter(label="date", field_name="updated", lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Appointment
        fields = ['type','name','updated']
