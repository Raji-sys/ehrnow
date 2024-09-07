from .models import *
from django.contrib import admin


@admin.register(HematologyTest)
class HematologyTestAdmin(admin.ModelAdmin):
    list_display = ('name','reference_range','price',)


@admin.register(ChempathTest)
class ChempathTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference_range', 'price',)


@admin.register(MicrobiologyTest)
class MicroTestAdmin(admin.ModelAdmin):
    list_display = ('name','reference_range','price')


@admin.register(SerologyTest)
class SerologyTestNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference_range','price')

