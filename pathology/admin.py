from .models import *
from django.contrib import admin


@admin.register(HematologyTest)
class HematologyTestAdmin(admin.ModelAdmin):
    list_display = ('name','reference_range','price',)


@admin.register(HematologyResult)
class HematologyResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test', 'result',  'created','updated',)


@admin.register(ChempathTestName)
class ChempathTestNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference_range', 'price',)


@admin.register(ChemicalPathologyResult)
class ChempathResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test', 'result',  'created','updated',)


@admin.register(MicrobiologyResult)
class MicroResultAdmin(admin.ModelAdmin):
    list_display = ('patient', 'test', 'result',  'created','updated',)


@admin.register(MicrobiologyTest)
class MicroTestAdmin(admin.ModelAdmin):
    list_display = ('name','reference_range','price')


@admin.register(SerologyResult)
class SerologyTestResultAdmin(admin.ModelAdmin):
    list_display = ('result_code', 'test', 'patient', 'result', 'comments')
    list_filter = ('test', 'patient')


@admin.register(SerologyTestName)
class SerologyTestNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference_range','price')
