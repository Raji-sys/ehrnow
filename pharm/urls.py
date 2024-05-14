from django.urls import path,include
from . import views 
from .views import *


urlpatterns=[
    path('',views.index, name='index'),
    path('login/',CustomLoginView.as_view(), name='signin'),
    path('create_drug/', views.create_drug, name='create_drug'),
    path('create_record/', views.create_record, name='create_record'),
    path('',include('django.contrib.auth.urls')),

    path('record/', views.records, name='record'),
    path('get_drugs_by_category/<int:category_id>/', views.get_drugs_by_category, name='get_drugs_by_category'),
    path('list/', views.drugs_list, name='list'),
    path('report/', views.reports, name='report'),
    path('drug_report/', views.drug_report, name='drug_report'),
    path('record_report/', views.record_report, name='record_report'),
    path('worth/', views.worth, name='worth'),

    path('drug_pdf/', views.drug_pdf, name='drug_pdf'),

    path('record_pdf/', views.record_pdf, name='record_pdf'),

]
