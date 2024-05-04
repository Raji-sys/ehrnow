from django import forms
from .models import *
from django.contrib import admin

admin.site.site_header="cPANEL"
admin.site.index_title="EHR NOW"
admin.site.site_title="EHR NOW"


@admin.register(PatientData)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'gender', 'dob', 'phone',)
    search_fields = ('file_no',)
    list_filter = ('gender',)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('patient', 'clinic', 'payment')
    search_fields = ('patient',)
    list_filter = ('patient__file_no',)


@admin.register(Paypoint)
class PaypointAdmin(admin.ModelAdmin):
    list_display = ('patient', 'service', 'status')
    search_fields = ('status',)
    list_filter = ('status',)
