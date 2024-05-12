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
 
    path('get-started/clinic-dashboard/', ClinicDashView.as_view(), name='clinic_list'),
    path('get-started/radiology', RadiologyView.as_view(), name='radiology'),
    path('get-started/phatology', PhatologyView.as_view(), name='phatology'),
 
    path('get-started/pharmacy', PharmacyView.as_view(), name='pharmacy'),
    path('get-started/physio', PhysioView.as_view(), name='physio'),
    path('get-started/theatre', TheatreView.as_view(), name='theatre'),
 
    path('get-started/ward', WardView.as_view(), name='ward'),
    path('get-started/icu', ICUView.as_view(), name='icu'),
    path('get-started/audit', AuditView.as_view(), name='audit'),

    # Record URLs
    path('medical-record/patient-movement/', PatientMovementView.as_view(), name='patient_movement'),
    path('record/create-patient/', PatientCreateView.as_view(), name='new_patient'),
    path('record/patient-list/', PatientListView.as_view(), name='patient_list'),
    path('record/patient-report/', PatientReportView.as_view(), name='patient_report'),
    path('record/patient/update-patient/<int:pk>/', UpdatePatientView.as_view(), name='update_patient'),
    path('record/create-appointment/<str:file_no>/', AppointmentCreateView.as_view(), name='new_appointment'),
    path('record/appointments/', AppointmentListView.as_view(), name='appointments'),
    path('record/appointment/update-appointment/<int:pk>/', AppointmentUpdateView.as_view(), name='update_appointment'),
    path('record/patient/<str:file_no>/', PatientFolderView.as_view(), name='patient_details'),
    path('record/patient/follow-up/<str:file_no>/', FollowUpVisitCreateView.as_view(), name='follow_up'),

    # Payment Clerk URLs
    path('revenue/paypoint-dash/record/', RevenueRecordView.as_view(), name='record_revenue'),
    path('revenue/paypoint/<str:file_no>/', PaypointView.as_view(), name='paypoint'),
    path('revenue/paypoint-dash/', PaypointDashboardView.as_view(), name='paypoint_dash'),

    path('revenue/follow-up/<str:file_no>/', PaypointFollowUpView.as_view(), name='paypoint_follow_up'),
    path('revenue/follow-up/', PaypointFollowUpDashboardView.as_view(), name='follow_up_pay_dash'),
    

    path('get-started/service-dash', ServiceView.as_view(), name='service_dash'),
    path('revenue/add-service/', ServiceCreateView.as_view(), name='add_service'),
    path('revenue/service-list/', ServiceListView.as_view(), name='service_list'),
    path('revenue/update-service/<int:pk>/', ServiceUpdateView.as_view(), name='update_service'),
    path('get-started/revenue/transactions/', TransactionView.as_view(), name='transaction_dash'),
    path('revenue/add-payment/', PayCreateView.as_view(), name='add_pay'),
    path('revenue/payment-list/', PayListView.as_view(), name='pay_list'),
    path('revenue/update-payment/<int:pk>/', ServiceUpdateView.as_view(), name='update_pay'),

    #VITALS
    path('nursing-station/vital_signs/<str:file_no>/', VitalSignCreateView.as_view(), name='vital_signs'),

    # AE
    path('nursing/nursing-station-ae/', AENursingDeskView.as_view(), name='nursing_station_ae'),

    # Consultation
    path('clinic/ae/', AEClinicDetailView.as_view(), name='ae_details'),

    path('clinic/ae/waiting-for-consultation/', AEConsultationWaitRoomView.as_view(), name="waiting_for_consultation_ae"),
    path('clinic/ae/waiting-for-consultation/room-1/', AERoom1View.as_view(), name="ae_room_1"),
    path('clinic/ae/waiting-for-consultation/room-2/', AERoom2View.as_view(), name="ae_room_2"),
    path('waiting-consultation/ae/clinical_note/<str:file_no>/', ClinicalNoteCreateView.as_view(), name='clinical_note'),
    path('clinic/ae/ae-consultation-finished/', AEConsultationFinishView.as_view(), name="consultation_finished_ae"),
    path('clinic/ae/ae-awaiting-review/', AEAwaitingReviewView.as_view(), name="waiting_for_review_ae"),
   
    #SOPD
    path('nursing/nursing-station-sopd/', SOPDNursingDeskView.as_view(), name='nursing_station_sopd'),

    # Consultation
    path('clinic/sopd/', SOPDClinicDetailView.as_view(), name='sopd_details'),

    path('clinic/sopd/waiting-for-consultation/', SOPDConsultationWaitRoomView.as_view(), name="waiting_for_consultation_sopd"),
    path('clinic/sopd/waiting-for-consultation/room-1/', SOPDRoom1View.as_view(), name="sopd_room_1"),
    path('clinic/sopd/waiting-for-consultation/room-2/', SOPDRoom2View.as_view(), name="sopd_room_2"),
    path('waiting-consultation/sopd/clinical_note/<str:file_no>/', ClinicalNoteCreateView.as_view(), name='clinical_note'),
    path('clinic/sopd/sopd-consultation-finished/', SOPDConsultationFinishView.as_view(), name="consultation_finished_sopd"),
    path('clinic/sopd/sopd-awaiting-review/', SOPDAwaitingReviewView.as_view(), name="waiting_for_review_sopd"),
    
    # path('report/', views.report, name='report'),

    # path('gen_report/', GenReportView.as_view(), name='gen_report'),
    # path('gen_pdf/', views.Gen_pdf, name='gen_pdf'),
    # path('gen_csvFile/', views.Gen_csv, name='gen_csv'),


    # path('stats/', StatsView.as_view(), name='stats'),
    # path('notice/', NoticeView.as_view(), name='notice'),
]
