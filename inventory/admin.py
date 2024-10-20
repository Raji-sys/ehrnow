from django import forms
from .models import *
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from import_export.admin import ImportMixin


admin.site.site_header="ADMIN PANEL"
admin.site.index_title="STORE INVENTORY MANAGEMENT SYSTEM"

    
class ItemAdminForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name','unit_price','qty','unit','vendor','expiration_date']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(ReStock)
class ReStockAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity_purchased', 'purchase_date', 'expiration_date')

    def item_name(self, obj):
        return obj.item.name
    
    item_name.short_description = 'Item Name'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    form=ItemAdminForm
    readonly_fields=('unit_price','qty')
    exclude=('added_by','balance','total_value')
    list_display = ['name','total_value','qty','vendor','unit_price','unit','current_balance','expiration_date', 'added_by', 'date_added','updated_at']
    list_filter = ['date_added','unit','added_by']
    search_fields = ['name']
    list_per_page=10
    ordering = ['name']

    def total_value(self, obj):
        return obj.total_value

    total_value.short_description = 'Total Value'

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by=request.user
        obj.save()


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    exclude = ('issued_by', 'balance')
    list_display = ['item', 'item_date', 'issued_to', 'issued_by_username','quantity','balance','date_issued','updated_at']
    search_fields = ['item', 'issued_to','item__vendor','item__date_added']
    list_filter = ['issued_to', 'item','item__vendor','item__date_added']
    list_per_page = 5

    def save_model(self, request, obj, form, change):
        try:
            obj.issued_by = request.user
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            messages.error(request, f"Error: {e.message}")

    def item_date(self, obj):
        return obj.item.date_added

    def issued_by_username(self, obj):
        return obj.issued_by.username if obj.issued_by else None

    issued_by_username.short_description = "Issued By"
