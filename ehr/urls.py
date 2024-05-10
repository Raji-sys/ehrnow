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

    # Receptionist URLs
    path('medical-record/patient-movement/', PatientMovementView.as_view(), name='patient_movement'),
    path('record/create-patient/', PatientCreateView.as_view(), name='new_patient'),
    path('record/patient-list/', PatientListView.as_view(), name='patient_list'),
    path('record/patient/<str:file_no>/', PatientFolderView.as_view(), name='patient_details'),
    path('record/patient/update-patient/<int:pk>/', UpdatePatientView.as_view(), name='update_patient'),
    path('record/patient/follow-up/<int:pk>/', FollowUpVisitCreateView.as_view(), name='follow_up'),

    # path('follow-up-patients-waiting-payment/', FollowUpPayListView.as_view(), name='follow_up_pay_dash'),
    path('medical-record/patient-movement/record-dashboard/', RecordDashboardView.as_view(), name='record_dash'),



    # Payment Clerk URLs
    path('revenue/paypoint-dash/record/', RevenueRecordView.as_view(), name='record_revenue'),
    path('revenue/paypoint/<int:handover_id>/', PaypointView.as_view(), name='paypoint'),
    path('revenue/paypoint-follow-up/<int:handover_id>/', PaypointFollowUpView.as_view(), name='paypoint_follow_up'),
    path('revenue/paypoint-dash/', PaypointDashboardView.as_view(), name='paypoint_dash'),

    #VITALS
    path('nursing-station/vital_signs/<str:file_no>/', VitalSignCreateView.as_view(), name='vital_signs'),

    # AE
    path('nursing/nursing-station/', AENursingDeskView.as_view(), name='nursing_station_ae'),

    # Consultation
    path('clinics/', AEClinicListView.as_view(), name='ae_clinic'),
    path('clinic/ae/', AEClinicDetailView.as_view(), name='ae_details'),
    path('clinic/room/<int:pk>/', RoomDetailView.as_view(), name='room_details'),

    path('clinic/ae/waiting-for-consultation/', AEConsultationWaitRoomView.as_view(), name="waiting_for_consultation_ae"),
    path('waiting-consultation/ae/clinical_note/<str:file_no>/', ClinicalNoteCreateView.as_view(), name='clinical'),
    path('clinic/ae/consultation-finished/', AEConsultationFinishView.as_view(), name="consultation_finished_ae"),
    path('clinic/ae/awaiting-review/', AEAwaitingReviewView.as_view(), name="waiting_for_review_ae"),
   
    #SOPD
    path('nursing/nursing-station-sopd/', SOPDNursingDeskView.as_view(), name='nursing_station_sopd'),

    # Consultation
    path('clinics/', SOPDClinicListView.as_view(), name='sopd_clinic'),
    path('clinic/sopd/', SOPDClinicDetailView.as_view(), name='sopd_details'),
    path('clinic/room/<int:pk>/', RoomDetailView.as_view(), name='room_details'),

    path('clinic/sopd/waiting-for-consultation/', SOPDConsultationWaitRoomView.as_view(), name="waiting_for_consultation_sopd"),
    path('waiting-consultation/sopd/clinical_note/<str:file_no>/', ClinicalNoteCreateView.as_view(), name='clinical_note'),
    path('clinic/consultation-finished/', SOPDConsultationFinishView.as_view(), name="consultation_finished_sopd"),
    path('clinic/awaiting-review/', SOPDAwaitingReviewView.as_view(), name="waiting_for_review_sopd"),
    
    # path('report/', views.report, name='report'),

    # path('gen_report/', GenReportView.as_view(), name='gen_report'),
    # path('gen_pdf/', views.Gen_pdf, name='gen_pdf'),
    # path('gen_csvFile/', views.Gen_csv, name='gen_csv'),


    # path('stats/', StatsView.as_view(), name='stats'),
    # path('notice/', NoticeView.as_view(), name='notice'),


]
