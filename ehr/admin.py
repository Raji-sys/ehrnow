from re import I
from .models import *
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin


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

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
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


from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget


class TheatreItemCategoryResource(resources.ModelResource):
    # Define the field to use name instead of ID
    name = fields.Field(
        column_name='name',
        attribute='name',
    )
    
    class Meta:
        model = TheatreItemCategory
        fields = ('name',)  # Only export/import the name field
        export_order = ('name',)
        import_id_fields = ('name',)  # Use name as the unique identifier for imports
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """
        Optional: Clean or validate data before import
        """
        if 'name' in row:
            row['name'] = row['name'].strip()  # Remove whitespace
        return super().before_import_row(row, **kwargs)


@admin.register(TheatreItemCategory)
class TheatreItemCategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TheatreItemCategoryResource
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    
    # Optional: Customize the import/export interface
    def get_export_queryset(self, request):
        """Optional: Filter what gets exported"""
        queryset = super().get_export_queryset(request)
        return queryset.order_by('name')


# If you need to reference this category from other models during import,
# you might also need a custom widget for foreign key relationships:
class TheatreItemCategoryWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        """
        Convert category name to category instance
        """
        if not value:
            return None
        try:
            return TheatreItemCategory.objects.get(name=value)
        except TheatreItemCategory.DoesNotExist:
            # Optionally create the category if it doesn't exist
            return TheatreItemCategory.objects.create(name=value)
        except TheatreItemCategory.MultipleObjectsReturned:
            # Handle duplicate names if they exist
            return TheatreItemCategory.objects.filter(name=value).first()

# TheatreItem Resource Class
class TheatreItemResource(resources.ModelResource):
    # Define category field to use name instead of ID
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=TheatreItemCategoryWidget(TheatreItemCategory, field='name')
    )
    
    name = fields.Field(
        column_name='name',
        attribute='name',
    )
    
    price = fields.Field(
        column_name='price',
        attribute='price',
    )
    
    class Meta:
        model = TheatreItem
        fields = ('category', 'name', 'price')
        export_order = ('category', 'name', 'price')
        import_id_fields = ('name',)  # Use name as unique identifier
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """Clean data before import"""
        # Clean name field
        if 'name' in row and row['name']:
            row['name'] = row['name'].strip()
        
        # Clean category field
        if 'category' in row and row['category']:
            row['category'] = row['category'].strip()
            
        # Clean price field
        if 'price' in row and row['price']:
            # Remove any currency symbols or spaces
            price_str = str(row['price']).strip()
            try:
                row['price'] = float(price_str)
            except ValueError:
                row['price'] = None
                
        return super().before_import_row(row, **kwargs)


@admin.register(TheatreItem)
class TheatreItemAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TheatreItemResource
    list_display = ('category', 'name', 'price')
    search_fields = ('category__name', 'name', 'price')  # Fixed typo: 'cateogry' -> 'category__name'
    list_filter = ('category', 'name', 'price')



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
    list_display = ('patient','theatre','notes','type_of_anaesthesia','findings','post_op_order','operated','updated')
    search_fields = ('patient','notes','type_of_anaesthesia','findings','post_op_order','operated','updated')
    list_filter = ('patient','notes','type_of_anaesthesia','findings','post_op_order','operated','updated')


@admin.register(TheatreOperationRecord)
class TheatreOperationRecordeAdmin(admin.ModelAdmin):
    list_display = ('patient','ward','theatre','updated')
    search_fields = ('patient','updated')
    list_filter = ('patient','updated')


@admin.register(AnaesthesiaChecklist)
class AnaesthisiaChecklistAdmin(admin.ModelAdmin):
    list_display = ('patient','doctor','updated')
    search_fields = ('doctor','updated')
    list_filter = ('doctor','updated')

@admin.register(PastSurgicalHistory)
class PastSurgicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('anaesthesia_checklist','id','surgery','when','where','LA_GA','outcome')


@admin.register(WardShiftNote)
class WardShiftNoteAdmin(admin.ModelAdmin):
    list_display = ('nurse','updated',)
    search_fields = ('nurse','updated')
    list_filter = ('nurse','updated')


@admin.register(PrivateTheatreItem)
class PrivateTheatreItemAdmin(ImportExportModelAdmin,admin.ModelAdmin):
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
    search_fields = ('seen','vitals','review','consultation','updated','created')
    ordering = ('-updated',)
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

@admin.register(RadiologyResult)
class RadiologyResultAdmin(admin.ModelAdmin):
    list_display = ('id','patient')

@admin.register(PhysioRequest)
class PhysioRequestAdmin(admin.ModelAdmin):
    list_display = ('id','patient')
