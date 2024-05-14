from tabnanny import verbose
import django_filters
from .models import Drug, Record
from django import forms


class DrugFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label="DRUG",field_name='name', lookup_expr='iexact')    
    # date_added = django_filters.DateFilter(label="DATE ADDED",field_name='date_added',lookup_expr='exact',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    date_added1 = django_filters.DateFilter(label="DATE ADDED R1",field_name='date_added',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])    
    date_added2 = django_filters.DateFilter(label="DATE ADDED R2",field_name='date_added',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    generic_name = django_filters.CharFilter(label="GENERIC NAME",field_name='generic_name', lookup_expr='iexact')
    brand_name = django_filters.CharFilter(label="BRAND NAME",field_name='brand_name', lookup_expr='iexact')
    category = django_filters.CharFilter(label="CLASS",field_name='category__name', lookup_expr='iexact')
    supplier = django_filters.CharFilter(label="SUPPLIER",field_name='supplier', lookup_expr='iexact')
    dosage_form = django_filters.CharFilter(label="DOSAGE FORM",field_name='dosage_form', lookup_expr='iexact')
    pack_size = django_filters.CharFilter(label="PACK SIZE",field_name='pack_size', lookup_expr='iexact')
    expiration_date1 = django_filters.DateFilter(label="EXPIRY DATE R1",field_name='expiration_date',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    expiration_date2 = django_filters.DateFilter(label="EXPIRY DATE R2",field_name='expiration_date',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])        
    added_by = django_filters.CharFilter(label="ADDED BY",field_name='added_by__username', lookup_expr='iexact')
   
    class Meta:
        model = Drug
        exclude= ['date_added','total_value','pack_price','cost_price','updated_at','expiration_date','total_purchased_quantity',]


class RecordFilter(django_filters.FilterSet):
    date_issued1 = django_filters.DateFilter(label="DATE ISSUED R1",field_name='date_issued',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    date_issued2 = django_filters.DateFilter(label="DATE ISSUED R2",field_name='date_issued',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])    
    category = django_filters.CharFilter(label="CLASS",field_name='drug__category__name', lookup_expr='iexact')
    drug = django_filters.CharFilter(label="DRUG",field_name='drug__name', lookup_expr='iexact')
    supplier = django_filters.CharFilter(label="SUPPLIER",field_name='drug__supplier', lookup_expr='iexact')
    brand_name = django_filters.CharFilter(label="BRAND",field_name='drug__brand_name', lookup_expr='iexact')
    unit_issued_to = django_filters.CharFilter(label="UNIT ISSUED TO",field_name='unit_issued_to', lookup_expr='iexact')
    # quantity = django_filters.NumberFilter(label="QUANTITY ISSUED",field_name='quantity', lookup_expr='iexact')
    issued_by = django_filters.CharFilter(label="ISSUED BY",field_name='issued_by__username', lookup_expr='iexact')
    # date_added1 = django_filters.DateFilter(label="DATE ISSUED RANGE 1",field_name='updated_at',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])    
    # date_added2 = django_filters.DateFilter(label="DATE ISSUED RANGE 2",field_name='updated_at',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])

    class Meta:
        model = Record
        exclude= ['date_issued','balance','siv','srv','invoice_no','updated_at','remark','quantity']