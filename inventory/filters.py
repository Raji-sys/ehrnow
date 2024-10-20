import django_filters
from .models import Item, Record,Unit
from django import forms
from django.contrib.auth import get_user_model

class ItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label="ITEM",field_name='name', lookup_expr='icontains')    
    date_added = django_filters.DateFilter(label="DATE ADDED",field_name='date_added',lookup_expr='exact',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    date_added1 = django_filters.DateFilter(label="FROM DATE",field_name='date_added',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])    
    date_added2 = django_filters.DateFilter(label="TO DATE",field_name='date_added',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    expiration_date1 = django_filters.DateFilter(label="FROM EXP DATE",field_name='expiration_date',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    expiration_date2 = django_filters.DateFilter(label="TO EXP DATE",field_name='expiration_date',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])        
    vendor = django_filters.CharFilter(label="VENDOR",field_name='vendor', lookup_expr='iexact')
    added_by = django_filters.ModelChoiceFilter(
        label="ADDED BY",
        queryset=get_user_model().objects.filter(added_items__isnull=False).distinct().order_by('username'),
        field_name='added_by',
        lookup_expr='exact',
        widget=forms.Select(attrs={
            'class': 'w-full text-center text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 text-indigo-800 rounded shadow-sm border border-gray-300 p-2'
        })
    )
    unit = django_filters.ModelChoiceFilter(
    label="STORE UNIT", 
    queryset=Unit.objects.all(), 
    widget=forms.Select(attrs={
        'class': 'w-full text-center text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 text-indigo-800 rounded shadow-sm border border-gray-300 p-2'
    })
) 
    class Meta:
        model = Item
        exclude= ['total_value','unit_price','updated_at','expiration_date','qty']


class RecordFilter(django_filters.FilterSet):
    date_issued = django_filters.DateFilter(label="DATE ISSUED",field_name='date_issued',lookup_expr='exact',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    item = django_filters.CharFilter(label="ITEM",field_name='item__name', lookup_expr='iexact')
    unit = django_filters.ModelChoiceFilter(
    label="STORE UNIT", 
    queryset=Unit.objects.all(), 
    widget=forms.Select(attrs={
        'class': 'w-full text-center text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 text-indigo-800 rounded shadow-sm border border-gray-300 p-2'
    }))
    vendor = django_filters.CharFilter(label="VENDOR",field_name='item__vendor', lookup_expr='iexact')
    issued_to = django_filters.CharFilter(label="ISSUED TO",field_name='issued_to', lookup_expr='iexact')
    quantity = django_filters.NumberFilter(label="QUANTITY ISSUED",field_name='quantity', lookup_expr='iexact')
    issued_by = django_filters.ModelChoiceFilter(
        label="ADDED BY",
        queryset=get_user_model().objects.filter(item_records__isnull=False).distinct().order_by('username'),
        field_name='issued_by',
        lookup_expr='exact',
        widget=forms.Select(attrs={
            'class': 'w-full text-center text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 text-indigo-800 rounded shadow-sm border border-gray-300 p-2'
        })
    )
    date_added1 = django_filters.DateFilter(label="FROM DATE",field_name='updated_at',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])    
    date_added2 = django_filters.DateFilter(label="TO DATE",field_name='updated_at',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Record
        exclude= ['balance','updated_at']