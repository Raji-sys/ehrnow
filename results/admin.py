from .models import *
from django.contrib import admin

# @admin.register(AsoTitre)
# class Testingdmin(admin.ModelAdmin):
#     list_display = ('id',)



@admin.register(GenericTest)
class GenericTestAdmin(admin.ModelAdmin):
    list_display = ('lab','name', 'price')
    search_fields = ('lab','name','price')
    list_filter = ('lab','name','price')

@admin.register(TestHandler)
class TestHandlerAdmin(admin.ModelAdmin):
    list_display = ('patient', 'lab','test', 'updated', 'id')
    list_filter = ('patient', 'lab','test', 'updated', 'id')


@admin.register(Testinfo)
class TestinfoAdmin(admin.ModelAdmin):
    list_display = ('patient', 'code', 'updated', 'id', 'payment_status',)
    list_filter = ('payment__status', 'cleared')  # Add filters

    @admin.display(ordering='payment__status', description='Payment')
    def payment_status(self, obj):
        if obj.payment:
            return '✓' if obj.payment.status else '✗'
        return '—'

    # Optionally add search
    search_fields = ('code', 'patient__name')  # Adjust based on your PatientData model fields
# @admin.register(Testinfo)
# class TestinfoAdmin(admin.ModelAdmin):
#     list_display = ('patient', 'code','updated','id', 'payment_status',)

#     @admin.display(ordering='payment__status', description='Payment')
#     def payment_status(self, obj):
#         return obj.payment.status if obj.payment.status else ''

    # list_display = ('patient', 'payment_status', 'code', 'test_lab', 'test_name', 'test_price')
    # @admin.display(ordering='payment__unit', description='Lab')
    # def test_lab(self, obj):
    #     return obj.payment.unit if obj.payment.unit else ''
    
    # @admin.display(ordering='payment__unit', description='Test')
    # def test_name(self, obj):
    #     return obj.payment.service if obj.payment.service else ''

    # @admin.display(ordering='payment__price', description='Cost')
    # def test_price(self, obj):
    #     return obj.payment.price if obj.payment.price else ''

