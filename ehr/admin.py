from .models import *
from django.contrib import admin


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'status', 'ward','payment','created','updated')
    search_fields = ('patient', 'status', 'ward','created','updated')
    list_filter = ('patient', 'status', 'ward','created','updated')

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'price')
    search_fields = ('type','name')
    list_filter = ('type','name')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(PatientData)
class PatientDataAdmin(admin.ModelAdmin):
    list_display = ('title','last_name','first_name','other_name','gender','age','updated')
    search_fields = ('title','last_name','first_name','other_name','gender','age','updated')
    list_filter = ('title','last_name','first_name','other_name','gender','age','updated')


@admin.register(Paypoint)
class PaypointAdmin(admin.ModelAdmin):
    list_display = ('patient','service','price','status')

@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('id',)
    search_fields = ('id',)
    list_filter = ('id',)

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id',)
    search_fields = ('id',)
    list_filter = ('id',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name','price')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('name','price')


@admin.register(TheatreItem)
class TheatreItemAdmin(admin.ModelAdmin):
    list_display = ('category','name','price')
    search_fields = ('cateogry','name','price')
    list_filter = ('category','name','price')


@admin.register(TheatreItemCategory)
class TheatreItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(RadiologyTest)
class RadiologyTestAdmin(admin.ModelAdmin):
    list_display = ('name','price','updated')
    search_fields = ('name','updated')
    list_filter = ('name','updated')


@admin.register(TheatreBooking)
class TheatreBookingAdmin(admin.ModelAdmin):
    list_display = ('patient','theatre','team','date','blood_requirement','updated')
    search_fields = ('patient','theatre','team','date','blood_requirement','updated')
    list_filter = ('patient','theatre','team','date','blood_requirement','updated')


@admin.register(OperationNotes)
class OperationNotesAdmin(admin.ModelAdmin):
    list_display = ('patient','notes','type_of_anaesthesia','findings','post_op_order','operated','updated')
    search_fields = ('patient','notes','type_of_anaesthesia','findings','post_op_order','operated','updated')
    list_filter = ('patient','notes','type_of_anaesthesia','findings','post_op_order','operated','updated')


@admin.register(TheatreOperationRecord)
class TheatreOperationRecordeAdmin(admin.ModelAdmin):
    list_display = ('patient','updated')
    search_fields = ('patient','updated')
    list_filter = ('patient','updated')


@admin.register(AnaesthisiaChecklist)
class AnaesthisiaChecklistAdmin(admin.ModelAdmin):
    list_display = ('patient','doctor','updated')
    search_fields = ('doctor','updated')
    list_filter = ('doctor','updated')

@admin.register(MedicalIllness)
class MedicalIllnesstAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    # filter_horizontal = ('concurrent_medical_illnesses',)

@admin.register(WardShiftSUmmaryNote)
class WardShiftSUmmaryNoteAdmin(admin.ModelAdmin):
    list_display = ('nurse','updated',)
    search_fields = ('nurse','updated')
    list_filter = ('nurse','updated')


@admin.register(PrivateTheatreItem)
class PrivateTheatreItemAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet','amount','transaction_type','description')
    search_fields = ('wallet','transaction_type')
    list_filter = ('wallet','transaction_type')
    readonly_fields=('wallet','amount','transaction_type','description')

@admin.register(Consumable)
class ConsumableAdmin(admin.ModelAdmin):
    list_display = ('name','cost','updated')
    search_fields = ('name','cost','updated')
    list_filter = ('name','cost','updated')


@admin.register(Implant)
class ImplantAdmin(admin.ModelAdmin):
    list_display = ('name','cost','updated')
    search_fields = ('name','cost','updated')
    list_filter = ('name','cost','updated')


@admin.register(VisitRecord)
class VisitRecordAdmin(admin.ModelAdmin):
    list_display = ('patient','clinic','team','seen','vitals','review','consultation','updated','created')
    search_fields = ('clinic','team','updated')
    list_filter = ('clinic','team','updated')


@admin.register(ClinicalNote)
class ClinicalNoteAdmin(admin.ModelAdmin):
    list_display = ('patient','note','diagnosis','user','updated')
    search_fields = ('patient','note','diagnosis','updated')
    list_filter = ('patient','note','diagnosis','updated')


@admin.register(PhysioTest)
class PhysioTestAdmin(admin.ModelAdmin):
    list_display = ('category','name','price','updated')
    search_fields = ('category','name','updated')
    list_filter = ('category','name','updated')
