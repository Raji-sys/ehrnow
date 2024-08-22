from django.urls import path, include
from .views import *
from django.urls import path
from . import views


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
 
    path('get-started/clinic-dashboard/', ClinicDashView.as_view(), name='clinic_list'),
    path('get-started/radiology', RadiologyView.as_view(), name='radiology'),
 
    path('get-started/pharmacy', PharmacyView.as_view(), name='pharmacy'),
    path('get-started/physio', PhysioView.as_view(), name='physio'),
    path('get-started/theatre', TheatreListView.as_view(), name='theatre'),
 
    path('get-started/ward/', WardListView.as_view(), name='ward_list'),
    path('get-started/audit', AuditView.as_view(), name='audit'),
    path('get-started/store', StoreView.as_view(), name='store'),

    # Record URLs
    path('medical-record/patient-movement/', PatientMovementView.as_view(), name='patient_movement'),
    path('medical-record/appointment-dash/', AppointmentDashboardView.as_view(), name='appt_dashboard'),

    path('record/create-patient/', PatientCreateView.as_view(), name='new_patient'),
    path('record/patient-list/', PatientListView.as_view(), name='patient_list'),
    path('record/patient/update-patient/<int:pk>/', UpdatePatientView.as_view(), name='update_patient'),
    path('record/patient/<str:file_no>/', PatientFolderView.as_view(), name='patient_details'),

    path('record/follow-up/', FollowUpListView.as_view(), name='follow_up_list'),
    path('record/patient/follow-up/<str:file_no>/', FollowUpVisitCreateView.as_view(), name='follow_up'),

    path('record/patient-report/', PatientReportView.as_view(), name='patient_report'),
    path('record/report/pdf', views.patient_report_pdf, name='patient_report_pdf'),
    path('record/statistics/', PatientStatsView.as_view(), name='patient_stats'),

    path('record/create-appointment/<str:file_no>/', AppointmentCreateView.as_view(), name='new_appointment'),
    path('record/appointments/', AppointmentListView.as_view(), name='appointments'),
    path('record/appointment/update-appointment/<int:pk>/', AppointmentUpdateView.as_view(), name='update_appointment'),
    path('record/appointment/new-appointment/', NewAppointmentListView.as_view(), name='new_appt_list'),


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
    
    path('revenue/hospital-services/', HospitalServicesListView.as_view(), name='hospital_services'),

    path('revenue/add-payment/', PayCreateView.as_view(), name='add_pay'),
    path('revenue/medical-record-list/', MedicalRecordPayListView.as_view(), name='record_pay_list'),
    path('revenue/pathology-list/', PathologyPayListView.as_view(), name='pathology_pay_list'),
    path('revenue/radiology-list/', RadiologyPayListView.as_view(), name='radiology_pay_list'),
    path('revenue/billing-list/', BillingPayListView.as_view(), name='bill_pay_list'),
    path('revenue/pharm-list/', PharmPayListView.as_view(), name='pharm_pay_list'),
    path('revenue/payment-list/', PayListView.as_view(), name='pay_list'),
    path('revenue/update-payment/<int:pk>/', PayUpdateView.as_view(), name='update_pay'),
    path('revenue/receipt/', views.receipt_pdf, name='receipt_pdf'),
    
    #VITALS
    path('nursing-station/vital_signs/<str:file_no>/', VitalSignCreateView.as_view(), name='vital_signs'),
    path('nursing-desks/', NursingDeskListView.as_view(), name='nursing_desks_list'),
    path('nursing-station/<int:pk>/', NursingStationDetailView.as_view(), name='nursing_station_detail'),
    # AE
    # path('nursing/nursing-station-ae/', AENursingDeskView.as_view(), name='nursing_station_ae'),
    # Consultation
    path('clinics/', ClinicDashView.as_view(), name='clinic_list'),
    path('clinic/<int:pk>/', ClinicDetailView.as_view(), name='clinic_details'),
    path('clinic/room/<int:pk>/', RoomDetailView.as_view(), name='room'),
    path('clinic/<int:clinic_id>/patients/<str:status>/', views.PTListView.as_view(), name='pt_list'),

    path('waiting-consultation/clinical_note/<str:file_no>/', ClinicalNoteCreateView.as_view(), name='clinical_note'),
    path('waiting-consultation/clinical_note_update/<int:pk>/', ClinicalNoteUpdateView.as_view(), name='clinical_note_update'),
   
    path('clinic/report/', PatientHandoverReportView.as_view(), name='handover_report'),
    path('clinic/report/pdf', views.clinic_handover_pdf, name='clinic_handover_pdf'),


    #admission
    path('clinic/admit-patient/<str:file_no>/', AdmissionCreateView.as_view(), name='admit_patient'),
    # path('clinic/admission-list/', AdmissionListView.as_view(), name='admission_list'),
    path('clinic/update-admission/<int:pk>/', AdmissionUpdateView.as_view(), name='receive_patient'),
    path('clinic/patient-discharge/<int:pk>/', AdmissionDischargeView.as_view(), name='discharge_patient'),
    
    #wards    
    path('ward/<int:pk>/',WardDetailView.as_view(), name='ward_details'),
    path('ward/<int:ward_id>/<str:status>/', GenericWardListView.as_view(), name='admission_list'),
 
    path('ward/nursing/vital-signs/<str:file_no>/', WardVitalSignCreateView.as_view(), name='ward_vital_signs'),
    path('ward/nursing/medication/<str:file_no>/', WardMedicationCreateView.as_view(), name='ward_medication'),
    path('ward/nursing/notes/<str:file_no>/', WardNotesCreateView.as_view(), name='ward_notes'),

    #theatre
    path('theatre/theatre-details/<int:pk>/', TheatreDetailView.as_view(), name='theatre_details'),
    
    path('clinic/theatre-booking/book-for-surgery/<str:file_no>/', TheatreBookingCreateView.as_view(), name='book_for_surgery'),
    path('clinic/<int:theatre_id>/theatre-booking/surgery-wait-list/', TheatreBookingListView.as_view(), name="surgery_wait_list"),
    path('clinic/theatre-booking/updating-boking/<int:pk>/', TheatreBookingUpdateView.as_view(), name='update_theatre_booking'),
    
    path('theatre-operation-record/create/<str:file_no>/', TheatreOperationRecordCreateView.as_view(), name='theatre_operation_record'),
    path('theatre/<int:theatre_id>/theatre-operation-record-list/', TheatreOperationRecordListView.as_view(), name="theatre_operation_record_list"), 
    
    path('theatre/theatre-notes/<str:file_no>/', OperationNotesCreateView.as_view(), name='operation_notes'),
    path('theatre/<int:theatre_id>/operated-patient-list/', OperationNotesListView.as_view(), name="operated_list"),

    path('theatre/anaesthesia-checklist/<str:file_no>/', AnaesthesiaChecklistCreateView.as_view(), name='anaesthesia_checklist'),
    path('theatre/<int:theatre_id>/anaesthesia-checklist_list/', AnaesthesiaChecklistListView.as_view(), name="anaesthesia_checklist_list"),

    #radiology
    path('radiology-list/', RadiologyListView.as_view(), name='radiology_list'),
    path('radiology-request/', RadiologyRequestListView.as_view(), name='radiology_request'),
    path('radiology-test/create/<str:file_no>/', RadiologyTestCreateView.as_view(), name='radiology_test'),
    path('radiology-result/create/<str:file_no>/<int:pk>/', RadiologyResultCreateView.as_view(), name='radiology_result'),
    path('radiology-report/', RadioReportView.as_view(), name='radiology_report'),

    #billing
    path('theatre/theatre-bill/<str:file_no>/', BillingCreateView.as_view(), name='surgery_bill'),   
    path('get_category/<int:category_id>/', views.get_category, name='get_category'),
    path('bill/<int:pk>/', BillDetailView.as_view(), name='bill_detail'),
    path('bills/', BillListView.as_view(), name='bill_list'),
    path('bill/pdf/<int:pk>/', BillPDFView.as_view(), name='bill_pdf'),
    
    #private billing
    path('theatre/theatre-private-bill/<str:file_no>/', PrivateBillingCreateView.as_view(), name='private_surgery_bill'),   
    path('private-bill/<int:pk>/', PrivateBillDetailView.as_view(), name='private_bill_detail'),
    path('private-bills/', PrivateBillListView.as_view(), name='private_bill_list'),
    path('private-bill/pdf/<int:pk>/', PrivateBillPDFView.as_view(), name='private_bill_pdf'),
   
    #wallet
    path('patient/<int:patient_pk>/fund-wallet/', FundWalletView.as_view(), name='fund_wallet'),
    path('revenue/wallet/transactions/', AllTransactionsListView.as_view(), name='all_transactions'),
    # path('patient/<str:file_no>/transactions/', PatientTransactionsListView.as_view(), name='patient_transactions'),
    path('patient/add-archive/<str:file_no>/',ArchiveCreateView.as_view(),name='new_archive'),
    path('patient/updated-archive/<int:pk>/',ArchiveUpdateView.as_view(),name='update_archive'),
    path('patient/delete-archive/<int:pk>/', ArchiveDeleteView.as_view(), name='delete_archive'),
]