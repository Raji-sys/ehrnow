import django_filters
from .models import Item, Record
from django import forms


class ItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label="ITEM",field_name='name', lookup_expr='iexact')    
    date_added = django_filters.DateFilter(label="DATE ADDED",field_name='date_added',lookup_expr='exact',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    date_added1 = django_filters.DateFilter(label="DATE ADDED RANGE 1",field_name='date_added',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])    
    date_added2 = django_filters.DateFilter(label="DATE ADDED RANGE 2",field_name='date_added',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    expiration_date1 = django_filters.DateFilter(label="EXPIRY DATE RANGE 1",field_name='expiration_date',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    expiration_date2 = django_filters.DateFilter(label="EXPIRY DATE RANGE 2",field_name='expiration_date',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])        
    vendor = django_filters.CharFilter(label="VENDOR",field_name='vendor', lookup_expr='iexact')
    added_by = django_filters.CharFilter(label="ADDED BY",field_name='added_by__username', lookup_expr='iexact')
    unit = django_filters.CharFilter(label="STORE UNIT",field_name='unit__name', lookup_expr='iexact')
   
    class Meta:
        model = Item
        exclude= ['total_value','cost','updated_at','expiration_date','total_purchased_quantity','issued_to']


class RecordFilter(django_filters.FilterSet):
    date_issued = django_filters.DateFilter(label="DATE ISSUED",field_name='date_issued',lookup_expr='exact',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    item = django_filters.CharFilter(label="ITEM",field_name='item__name', lookup_expr='iexact')
    unit = django_filters.CharFilter(label="STORE UNIT",field_name='unit__name', lookup_expr='iexact')
    vendor = django_filters.CharFilter(label="VENDOR",field_name='item__vendor', lookup_expr='iexact')
    issued_to = django_filters.CharFilter(label="ISSUED TO",field_name='issued_to', lookup_expr='iexact')
    quantity = django_filters.NumberFilter(label="QUANTITY ISSUED",field_name='quantity', lookup_expr='iexact')
    issued_by = django_filters.CharFilter(label="ISSUED BY",field_name='issued_by__username', lookup_expr='iexact')
    date_added1 = django_filters.DateFilter(label="DATE ISSUED RANGE 1",field_name='updated_at',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])    
    date_added2 = django_filters.DateFilter(label="DATE ISSUED RANGE 2",field_name='updated_at',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Record
        exclude= ['balance','updated_at']