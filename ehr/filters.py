import django_filters
from django import forms
from .models import *

class StaffFilter(django_filters.FilterSet):
    last_name = django_filters.CharFilter(label='NAME', field_name='user__last_name', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['last_name']
