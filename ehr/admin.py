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
    list_display = ('patient', 'get_service_info', 'status')
    search_fields = ('status',)
    list_filter = ('status',)


@admin.register(ServiceType)
class ServicesTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


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
    list_display = ('patient','user','note',)
    search_fields = ('patient',)
    list_filter = ('patient',)

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
