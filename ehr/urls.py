from django.urls import path, include
from .views import *
from django.urls import path


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
 
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('get-started/', GetStartedView.as_view(), name='get_started'),
    path('',include('django.contrib.auth.urls')),

    path('documentation/<int:pk>/', DocumentationView.as_view(), name='doc'),
    path('staff/', StaffDashboardView.as_view(), name='staff'),
    path('stafflist/', StaffListView.as_view(), name='stafflist'),
    path('profile/<str:username>/',ProfileDetailView.as_view(), name='profile_details'),
    path('update-user/<int:pk>/', UpdateUserView.as_view(), name='update_user'),
    path('update-profile/<int:pk>/',UpdateProfileView.as_view(), name='update_profile'),
    
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
    path('record/create-patient/', PatientCreateView.as_view(), name='new_patient'),
    path('record/patientlist/', PatientListView.as_view(), name='patientlist'),
    path('record/patient/<str:file_no>/',PatientFolderView.as_view(), name='patient_folder'),
    path('record/patient/update-patient/<int:pk>/',UpdatePatientView.as_view(), name='update_patient'),
    path('record/patient/follow-up/<str:file_no>/', HandleVisitView.as_view(), name='follow_up'),

    path('record-dashboard/', RecordDashboardView.as_view(), name='record_dash'),
    # path('assign-clinic/<int:pk>/', views.AssignClinicView.as_view(), name='assign_clinic'),

    # # Payment Clerk URLs
    # path('revenue/paypoint/<int:handover_id>/', views.PaypointView.as_view(), name='paypoint'),
    # path('revenue/paypoint-dash/', views.PaypointDashboardView.as_view(), name='paypoint_dash'),

    # Doctor URLs

    # Other URLs for NursingDesk, ConsultationRoom, etc

    # path('patients/', views.PatientListView.as_view(), name='patient'),


    # path('report/', views.report, name='report'),

    # path('gen_report/', GenReportView.as_view(), name='gen_report'),
    # path('gen_pdf/', views.Gen_pdf, name='gen_pdf'),
    # path('gen_csvFile/', views.Gen_csv, name='gen_csv'),


    # path('stats/', StatsView.as_view(), name='stats'),
    # path('notice/', NoticeView.as_view(), name='notice'),


]
