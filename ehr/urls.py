from django.urls import path, include
from .views import *
from . import views

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
 
    # path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
 
    path('get-started/', GetStartedView.as_view(), name='get_started'),
 
    path('get-started/medical-record', MedicalRecordView.as_view(), name='medical_record'),
    path('get-started/revenue', RevenueView.as_view(), name='revenue'),
    path('get-started/nursing', NursingView.as_view(), name='nursing'),
 
    path('get-started/clinic', ClinicView.as_view(), name='clinic'),
    path('get-started/radiology', RadiologyView.as_view(), name='radiology'),
    path('get-started/phatology', PhatologyView.as_view(), name='phatology'),
 
    path('get-started/pharmacy', PharmacyView.as_view(), name='pharmacy'),
    path('get-started/physio', PhysioView.as_view(), name='physio'),
    path('get-started/theatre', TheatreView.as_view(), name='theatre'),
 
    path('get-started/ward', WardView.as_view(), name='ward'),
    path('get-started/icu', ICUView.as_view(), name='icu'),
    path('get-started/audit', AuditView.as_view(), name='audit'),
 
    # Receptionist URLs
    path('create-patient/', views.CreatePatientView.as_view(), name='create_patient'),
    path('receptionist-dashboard/', views.ReceptionistDashboardView.as_view(), name='receptionist_dashboard'),
    path('handle-appointment/<int:pk>/', views.HandleVisitView.as_view(), name='handle_appointment'),
    path('assign-clinic/<int:pk>/', views.AssignClinicView.as_view(), name='assign_clinic'),

    # Payment Clerk URLs
    path('payment/<int:handover_id>/', views.PaymentView.as_view(), name='payment'),
    path('payment-clerk-dashboard/', views.PaymentClerkDashboardView.as_view(), name='payment_clerk_dashboard'),

    # Doctor URLs

    # Other URLs for NursingDesk, ConsultationRoom, etc

    # path('patients/', PatientListView.as_view(), name='patient'),


    # path('report/', views.report, name='report'),

    # path('gen_report/', GenReportView.as_view(), name='gen_report'),
    # path('gen_pdf/', views.Gen_pdf, name='gen_pdf'),
    # path('gen_csvFile/', views.Gen_csv, name='gen_csv'),


    # path('stats/', StatsView.as_view(), name='stats'),
    # path('notice/', NoticeView.as_view(), name='notice'),


    # path('profile/<str:username>/',ProfileDetailView.as_view(), name='profile_details'),
    # path('update-user/<int:pk>/', UpdateUserView.as_view(), name='update_user'),
    # path('update-profile/<int:pk>/',UpdateProfileView.as_view(), name='update_profile'),

    # path('', include('django.contrib.auth.urls')),
]
