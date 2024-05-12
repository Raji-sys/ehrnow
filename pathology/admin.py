from .models import *
from django.contrib import admin

# admin.site.site_header="ADMIN PANEL"
# admin.site.index_title="PATHOLOGY MANAGEMENT SYSTEM"
# admin.site.site_title="SUPREME DIAGNOSTIC LABORATORIES"


@admin.register(HematologyTest)
class HematologyTestAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(HematologyResult)
class HematologyResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test', 'result',  'created','updated',)


@admin.register(ChempathTestName)
class ChempathTestNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference_range')


@admin.register(ChemicalPathologyResult)
class ChempathResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test', 'result',  'created','updated',)


@admin.register(MicrobiologyResult)
class MicroResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test', 'result',  'created','updated',)


@admin.register(MicrobiologyTest)
class MicroTestAdmin(admin.ModelAdmin):
    list_display = ('name','reference_range',)


@admin.register(SerologyResult)
class SerologyTestResultAdmin(admin.ModelAdmin):
    list_display = ('result_code', 'test', 'patient', 'result', 'comments')
    list_filter = ('test', 'patient')

    def display_parameters(self, obj):
            return ", ".join([f"{p.result.test} {p.name}: {p.value}" for p in obj.parameters.all()])

    display_parameters.short_description = "Parameters"

@admin.register(SerologyTestName)
class SerologyTestNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference_range')

