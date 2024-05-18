from .models import *
from django.contrib import admin


# admin.site.site_header="EHR NOW CONTROL PANEL"
# admin.site.index_title="EHR NOW"
# admin.site.site_title="EHR NOW"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','full_name','department','unit','phone')
    search_fields = ('unit',)
    list_filter = ('unit',)

@admin.register(PatientData)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'gender', 'dob', 'phone',)
    search_fields = ('file_no',)
    list_filter = ('gender',)


@admin.register(FollowUpVisit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('patient', 'clinic', 'payment')
    search_fields = ('patient',)
    list_filter = ('patient__file_no',)


@admin.register(Paypoint)
class PaypointAdmin(admin.ModelAdmin):
    list_display = ('patient', 'service','status')
    search_fields = ('status','service')
    list_filter = ('status','service')



@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'price')
    search_fields = ('type','name')
    list_filter = ('type','name')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('clinic','name',)
    search_fields = ('clinic','name')
    list_filter = ('clinic','name')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(ClinicalNote)
class ClinicNoteAdmin(admin.ModelAdmin):
    list_display = ('patient','user','note','diagnosis','needs_review','appointment')
    search_fields = ('patient','diagnosis','needs_review','appointment')
    list_filter = ('patient','diagnosis','needs_review','appointment')

@admin.register(PatientHandover)
class HandoverAdmin(admin.ModelAdmin):
    list_display = ('patient','status','clinic','room')
    search_fields = ('patient',)
    list_filter = ('patient',)


@admin.register(VitalSigns)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ('patient',)
    search_fields = ('patient',)
    list_filter = ('patient',)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('name','price')


@admin.register(TheatreItem)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ('name','price')
    search_fields = ('name','price')
    list_filter = ('name','price')


@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ('bill','item','quantity')
    search_fields = ('bill','item')
    list_filter = ('bill','item')

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('patient','date','total_cost')
    search_fields = ('patient','date')
    list_filter = ('patient','date')
