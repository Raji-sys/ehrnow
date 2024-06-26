from .models import *
from django.contrib import admin

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','full_name','department','unit','phone')
    search_fields = ('unit',)
    list_filter = ('unit',)

@admin.register(PatientData)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'age', 'phone',)
    search_fields = ('file_no','phone')
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
    list_display = ('patient','status','clinic','room','updated')
    search_fields = ('patient','updated')
    list_filter = ('patient','updated')


@admin.register(VitalSigns)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ('patient',)
    search_fields = ('patient',)
    list_filter = ('patient',)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('name','price')



@admin.register(Bill)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ('patient','total_amount','created')
    search_fields = ('patient','created')
    list_filter = ('patient','created')


@admin.register(TheatreItem)
class TheatreItemAdmin(admin.ModelAdmin):
    list_display = ('bill','name','price','quantity')
    search_fields = ('name','price','quantity')
    list_filter = ('name','price','quantity')


@admin.register(RadiologyTest)
class RadiologyTestAdmin(admin.ModelAdmin):
    list_display = ('name','price','updated')
    search_fields = ('name','updated')
    list_filter = ('name','updated')


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('patient','ward','bed_number','updated')
    search_fields = ('patient','ward','bed_number','updated')
    list_filter = ('patient','ward','bed_number','updated')


@admin.register(TheatreBooking)
class TheatreBookingAdmin(admin.ModelAdmin):
    list_display = ('patient','theatre','team','date','updated')
    search_fields = ('patient','theatre','team','date','updated')
    list_filter = ('patient','theatre','team','date','updated')


@admin.register(TheatreNotes)
class TheatreNotesAdmin(admin.ModelAdmin):
    list_display = ('patient','operation_notes','type_of_anaesthesia','findings','operated','updated')
    search_fields = ('patient','operation_notes','type_of_anaesthesia','findings','operated','updated')
    list_filter = ('patient','operation_notes','type_of_anaesthesia','findings','operated','updated')


