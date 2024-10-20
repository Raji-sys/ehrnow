from django.urls import path
from . import views 

app_name='inventory'
urlpatterns=[
    path('store-inventory',views.index, name='store_inventory'),
    path('create_item/', views.create_item, name='create_item'),
    path('create_record/', views.create_record, name='create_record'),
    path('restock/', views.restock, name='restock'),

    path('record/', views.records, name='record'),
    path('get_items_for_unit/', views.get_items_for_unit, name='get_items_for_unit'),
    path('list/', views.items_list, name='list'),
    path('item_report/', views.item_report, name='item_report'),
    path('record_report/', views.record_report, name='record_report'),
    path('worth/', views.worth, name='worth'),

    path('item_pdf/', views.item_pdf, name='item_pdf'),

    path('record_pdf/', views.record_pdf, name='record_pdf'),

]
