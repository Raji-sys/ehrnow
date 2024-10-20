from django import forms
from django.contrib import admin
from .models import *
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from import_export.admin import ImportMixin


admin.site.site_header="ADMIN PANEL"
admin.site.index_title="PHARMACY INVENTORY MANAGEMENT SYSTEM"

    
class DrugAdminForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = ['name','generic_name','brand_name','category','supplier','dosage_form','pack_price','pack_size','cost_price','total_purchased_quantity','expiration_date']  


# Create an admin class for the drug model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('drug', 'quantity_purchased', 'purchase_date')

    def drug_name(self, obj):
        return obj.drug.name
    
    drug_name.short_description = 'drug Name'


@admin.register(Drug)
class DrugAdmin(ImportMixin,admin.ModelAdmin):
    form=DrugAdminForm
    # readonly_fields=('total_purchased_quantity',)
    exclude=('added_by','balance','total_value')
    list_display = ['name','generic_name','brand_name','category','supplier','dosage_form','pack_size','pack_price','cost_price','total_purchased_quantity','current_balance','total_value','expiration_date','added_by', 'date_added','updated_at']
    list_filter = ['date_added','category','supplier','added_by']
    search_fields = ['name']
    list_per_page=10

    def total_value(self, obj):
        return obj.total_value

    total_value.short_description = 'Total Value'

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by=request.user
        obj.save()


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    exclude = ('issued_by', 'drug__current_balance')
    list_display = ['drug', 'unit_issued_to', 'issued_by_username', 'quantity','date_issued','updated_at']
    search_fields = ['drug', 'issued_to','drug__supplier','drug__date_added']
    list_filter = ['unit_issued_to', 'drug','drug__supplier','drug__date_added']
    list_per_page = 10

    def save_model(self, request, obj, form, change):
        try:
            obj.issued_by = request.user
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            messages.error(request, f"Error: {e.message}")

    def drug_date(self, obj):
        return obj.drug.date_added

    def issued_by_username(self, obj):
        return obj.issued_by.username if obj.issued_by else None

    issued_by_username.short_description = "Issued By"

