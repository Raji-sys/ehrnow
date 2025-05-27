from django.contrib import admin
from .models import *
from django.core.exceptions import ValidationError
from import_export.admin import ImportMixin
from simple_history.admin import SimpleHistoryAdmin
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin 
from import_export import resources, fields


class CaseInsensitiveForeignKeyWidget(ForeignKeyWidget):
    def get_queryset(self, value, row, *args, **kwargs):
        if not value:
            return self.model.objects.none()
        
        # Try exact match first (faster)
        exact_match = self.model.objects.filter(**{self.field: value})
        if exact_match.exists():
            return exact_match
        
        # Fall back to case-insensitive match
        return self.model.objects.filter(**{f"{self.field}__iexact": value})
    
    def clean(self, value, row=None, *args, **kwargs):
        """
        Override clean method to handle case where no match is found
        """
        if not value:
            return None
            
        qs = self.get_queryset(value, row, *args, **kwargs)
        
        if not qs.exists():
            # Log the issue (helpful for debugging)
            print(f"No match found for supplier: '{value}'")
            # Return None instead of raising an exception
            return None
            
        return qs.first()


@admin.register(CompanyExpense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'vendor', 'amount', 'account_used', 'payment_method', 'updated')
    list_filter = ('category', 'vendor', 'amount', 'account_used', 'payment_method','updated')
    search_fields = ('category', 'vendor', 'account_used')
    autocomplete_fields = ['account_used',]
    list_per_page = 10
    ordering = ('-updated',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'description', 'created', 'created_by')
    list_filter = ('transaction_type', 'created')
    search_fields = ('account__name', 'account__account_number', 'description')
    date_hierarchy = 'created'
    readonly_fields = ('created',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account', 'created_by')

@admin.register(CompanyAccount)
class CompanyAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number', 'balance', 'created', 'updated')
    search_fields = ('name', 'account_number')
    list_filter = ('created',)
    # readonly_fields = ('balance', 'created', 'updated')
    readonly_fields = ('created', 'updated')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('account_number',)
        return self.readonly_fields
    