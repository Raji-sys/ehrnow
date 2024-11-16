import django_filters
from django import forms
from .models import *


class GenFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(
        label='id',
        field_name="id",
        lookup_expr='iexact'
    )
    collected = django_filters.DateFilter(label="date collected", field_name="collected",lookup_expr='exact', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])   
    patient_no=django_filters.NumberFilter(label='pn', field_name="patient__file_no",lookup_expr='exact')
    name=django_filters.CharFilter(label='test',field_name="name",lookup_expr='iexact')                                                                                                     

    class Meta:
        model=GeneralTestResult
        fields=['collected','patient_no','name']

class PayFilter(django_filters.FilterSet):
    user=django_filters.CharFilter(label='STAFF', field_name="user__username",lookup_expr='iexact')
    patient=django_filters.CharFilter(label='FILE NO',field_name="patient__file_no",lookup_expr='iexact')                                                                                                     
    service=django_filters.CharFilter(label='SERVICE',field_name="service",lookup_expr='iexact')                                                                                                     
    unit=django_filters.CharFilter(label='UNIT',field_name="unit",lookup_expr='iexact')                                                                                                     
    created1 = django_filters.DateFilter(label="DATE1", field_name="created", lookup_expr='lte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    created2 = django_filters.DateFilter(label="DATE2", field_name="created", lookup_expr='gte', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Paypoint
        fields = ['user','patient','unit','service']


class TestFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(
        label='id',
        field_name="id",
        lookup_expr='iexact'
    )
    collected = django_filters.DateFilter(
        label="date collected",
        field_name="collected",
        lookup_expr='exact',
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y']
    )
    patient_no = django_filters.CharFilter(
        label='pn',
        field_name="patient__file_no",
        lookup_expr='exact'
    )

    class Meta:
        model = Testinfo
        fields = ['id','collected', 'patient_no',]