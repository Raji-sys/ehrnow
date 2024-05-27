from django.urls import path,include
from . import views 
from .views import *

app_name='pharm'

urlpatterns=[
    path('pharmacy/inventory/',views.pharm_inventory, name='pharm_inventory'),
    path('pharmacy/dispensary/',DispensaryView.as_view(), name='dispensary'),
    
    #Inventory
    path('create_drug/', views.create_drug, name='create_drug'),
    path('create_record/', views.create_record, name='create_record'),
    path('record/', views.records, name='record'),
    path('get_drugs_by_category/<int:category_id>/', views.get_drugs_by_category, name='get_drugs_by_category'),
    path('list/', views.drugs_list, name='list'),
    path('record_report/', views.record_report, name='record_report'),
    path('worth/', views.worth, name='worth'),
    path('drug_report/', views.drug_report, name='drug_report'),
    path('drug_pdf/', views.drug_pdf, name='drug_pdf'),
    path('record_pdf/', views.record_pdf, name='record_pdf'),

    # dispensary
    path('pharmacy/dispensary/add-dispense/<str:file_no>/', views.create_dispensary, name='add_dispense'),
    path('pharmacy/dispensary/dispensed/', DispenseListView.as_view(), name='dispensed_list'),
    
    #Prescription
    path('pharmacy/prescription/prescribe/<str:file_no>/', views.create_prescription, name='add_prescription'),
    path('pharmacy/prescription/prescribed/', PrescriptionListView.as_view(), name='prescription_list'),
    path('pharmacy/prescription/update/<int:pk>/', PrescriptionUpdateView.as_view(), name='update_prescription'),
    path('pharmacy/transaction/', PharmPayListView.as_view(), name='pharmacy_transaction'),

]
