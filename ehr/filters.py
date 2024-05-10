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

    class Meta:
        model = Appointment
        fields = ['patient__file_no','date','clinic','team']
