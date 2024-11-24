from django.urls import path, include
from .views import *
from . import views

app_name='results'

urlpatterns = [
    
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('report/', ReportView.as_view(), name='report'),
    path('print-pdf/', views.report_pdf, name='report_pdf'),

    path('instance-pdf/<int:id>/', views.instance_pdf, name='instance_pdf'),    
    path('revenue/pathology-pay-list/', PathologyPayListView.as_view(), name='lab_revenue'),

    path('hematology/', HematologyView.as_view(), name='hematology'),
    path('hematology-list/', HematologyListView.as_view(), name='hematology_list'),
    path('hematology-request/', HematologyRequestListView.as_view(), name='hematology_request'),
   
   
    path('chempath/', ChempathView.as_view(), name='chempath'),    
    path('chempath-list/',ChempathListView.as_view(),name='chempath_list'),
    path('chempath-request/',ChempathRequestListView.as_view(),name='chempath_request'),

    path('micro/', MicrobiologyView.as_view(), name='micro'),    
    path('micro-list/',MicroListView.as_view(),name='micro_list'),
    path('micro-request/',MicroRequestListView.as_view(),name='micro_request'),
    
    path('serology/', SerologyView.as_view(), name='serology'),    
    path('serology-list/',SerologyListView.as_view(),name='serology_list'),
    path('serology-request/',SerologyRequestListView.as_view(),name='serology_request'),
    
    path('general/', GeneralView.as_view(), name='general'),    
    path('general-list/',GeneralListView.as_view(),name='general_list'),
    path('general-request/',GeneralRequestListView.as_view(),name='general_request'),
    path('general-test/create/<str:file_no>/',GeneralTestCreateView.as_view(), name='general_test'),
    path('general-result/create/<str:file_no>/<int:pk>/',GeneralResultUpdateView.as_view(), name='general_result'),
    path('general-report/', GeneralReportView.as_view(), name='general_report'),
    path('general-pdf/', views.general_report_pdf, name='general_report_pdf'),

    # hematology 
    path('blood-group/create/<str:file_no>/', BloodGroupCreateView.as_view(), name='create_blood_group'),
    path('blood-group/update/<str:file_no>/<int:test_info_pk>/', BloodGroupUpdateView.as_view(), name='update_blood_group'),

    path('genotype/create/<str:file_no>/', GenotypeCreateView.as_view(), name='create_genotype'),
    path('genotype/update/<str:file_no>/<int:test_info_pk>/', GenotypeUpdateView.as_view(), name='update_genotype'),

    path('fbc/create/<str:file_no>/', FBCCreateView.as_view(), name='create_fbc'),
    path('fbc/update/<str:file_no>/<int:test_info_pk>/', FBCUpdateView.as_view(), name='update_fbc'),

    # chempath
    path('urea-electrolyte/create/<str:file_no>/', UECreateView.as_view(), name='create_urea_electrolyte'),
    path('urea-electrolyte/update/<str:file_no>/<int:test_info_pk>/', UreaAndElectrolyteUpdateView.as_view(), name='update_urea_electrolyte'),

    path('liver-function/create/<str:file_no>/', LiverFunctionCreateView.as_view(), name='create_liver_function'),
    path('liver-function/update/<str:file_no>/<int:test_info_pk>/', LiverFunctionUpdateView.as_view(), name='update_liver_function'),
    
    path('lipid-profile/create/<str:file_no>/', LipidProfileCreateView.as_view(), name='create_lipid_profile'),
    path('lipid-profile/update/<str:file_no>/<int:test_info_pk>/', LipidProfileUpdateView.as_view(), name='update_lipid_profile'),
    
    path('blood-glucose/create/<str:file_no>/', BloodGlucoseCreateView.as_view(), name='create_blood_glucose'),
    path('blood-glucose/update/<str:file_no>/<int:test_info_pk>/', BloodGlucoseUpdateView.as_view(), name='update_blood_glucose'),
    
    path('serum-proteins/create/<str:file_no>/', SerumProteinsCreateView.as_view(), name='create_serum_proteins'),
    path('serum-proteins/update/<str:file_no>/<int:test_info_pk>/', SerumProteinsUpdateView.as_view(), name='update_serum_proteins'),
    
    path('bone-chemistry/create/<str:file_no>/', BoneChemistryCreateView.as_view(), name='create_bone_chemistry'),
    path('bone-chemistry/update/<str:file_no>/<int:test_info_pk>/', BoneChemistryUpdateView.as_view(), name='update_bone_chemistry'),
    
    path('cerebro-spinal-fluid/create/<str:file_no>/', CerebroSpinalFluidCreateView.as_view(), name='create_cerebro_spinal_fluid'),
    path('cerebro-spinal-fluid/update/<str:file_no>/<int:test_info_pk>/', CerebroSpinalFluidUpdateView.as_view(), name='update_cerebro_spinal_fluid'),
    
    path('miscellaneous-chempath-tests/create/<str:file_no>/', MiscellaneousChempathTestsCreateView.as_view(), name='create_miscellaneous_chempath_tests'),
    path('miscellaneous-chempath-tests/update/<str:file_no>/<int:test_info_pk>/', MiscellaneousChempathTestsUpdateView.as_view(), name='update_miscellaneous_chempath_tests'),
    
    # serology 
    path('widal/create/<str:file_no>/', WidalCreateView.as_view(), name='create_widal'),
    path('widal/update/<str:file_no>/<int:test_info_pk>/', WidalUpdateView.as_view(), name='update_widal'),

    path('rheumatoid-factor/create/<str:file_no>/', RheumatoidFactorCreateView.as_view(), name='create_rheumatoid_factor'),
    path('rheumatoid-factor/update/<str:file_no>/<int:test_info_pk>/', RheumatoidFactorUpdateView.as_view(), name='update_rheumatoid_factor'),

    path('hpb/create/<str:file_no>/', HepatitisBCreateView.as_view(), name='create_hpb'),
    path('hpb-test/update/<str:file_no>/<int:test_info_pk>/', views.HepatitisBUpdateView.as_view(), name='update_hpb'),

    path('hcv/create/<str:file_no>/', HepatitisCCreateView.as_view(), name='create_hcv'),
    path('hcv/update/<str:file_no>/<int:test_info_pk>/', HepatitisCUpdateView.as_view(), name='update_hcv'),

    path('vdrl/create/<str:file_no>/', VDRLCreateView.as_view(), name='create_vdrl'),
    path('vdrl/update/<str:file_no>/<int:test_info_pk>/', VDRLUpdateView.as_view(), name='update_vdrl'),

    path('mantoux/create/<str:file_no>/', MantouxCreateView.as_view(), name='create_mantoux'),
    path('mantoux/update/<str:file_no>/<int:test_info_pk>/', MantouxUpdateView.as_view(), name='update_mantoux'),

    path('aso-titre/create/<str:file_no>/', AsoTitreCreateView.as_view(), name='create_aso_titre'),
    path('aso-titre/update/<str:file_no>/<int:test_info_pk>/', AsoTitreUpdateView.as_view(), name='update_aso_titre'),

    path('crp/create/<str:file_no>/', CRPCreateView.as_view(), name='create_crp'),
    path('crp/update/<str:file_no>/<int:test_info_pk>/', CRPUpdateView.as_view(), name='update_crp'),

    path('hiv-screening/create/<str:file_no>/', HIVScreeningCreateView.as_view(), name='create_hiv_screening'),
    path('hiv-screening/update/<str:file_no>/<int:test_info_pk>/', HIVScreeningUpdateView.as_view(), name='update_hiv_screening'),

    # microbiology
    path('urine-microscopy/create/<str:file_no>/', UrineMicroscopyCreateView.as_view(), name='create_urine_microscopy'),
    path('urine-microscopy/update/<str:file_no>/<int:test_info_pk>/', UrineMicroscopyUpdateView.as_view(), name='update_urine_microscopy'),

    path('hvs/create/<str:file_no>/', HVSCreateView.as_view(), name='create_hvs'),
    path('hvs/update/<str:file_no>/<int:test_info_pk>/', HVSUpdateView.as_view(), name='update_hvs'),

    path('stool/create/<str:file_no>/', StoolCreateView.as_view(), name='create_stool'),
    path('stool/update/<str:file_no>/<int:test_info_pk>/', StoolUpdateView.as_view(), name='update_stool'),

    path('blood-culture/create/<str:file_no>/', BloodCultureCreateView.as_view(), name='create_blood_culture'),
    path('blood-culture/update/<str:file_no>/<int:test_info_pk>/', BloodCultureUpdateView.as_view(), name='update_blood_culture'),

    path('occult-blood/create/<str:file_no>/', OccultBloodCreateView.as_view(), name='create_occult_blood'),
    path('occult-blood/update/<str:file_no>/<int:test_info_pk>/', OccultBloodUpdateView.as_view(), name='update_occult_blood'),

    path('sputum_mcs/create/<str:file_no>/', SputumMCSCreateView.as_view(), name='create_sputum_mcs'),
    path('sputum_mcs/update/<str:file_no>/<int:test_info_pk>/', SputumMCSUpdateView.as_view(), name='update_sputum_mcs'),

    path('swab_pus_aspirate_mcs/create/<str:file_no>/', SwabPusAspirateCreateView.as_view(), name='create_swab_pus_aspirate_mcs'),
    path('swab_pus_aspirate_mcs/update/<str:file_no>/<int:test_info_pk>/', SwabPusAspirateUpdateView.as_view(), name='update_swab_pus_aspirate_mcs'),

    path('gram-stain/create/<str:file_no>/', GramStainCreateView.as_view(), name='create_gram_stain'),
    path('gram-stain/update/<str:file_no>/<int:test_info_pk>/', GramStainUpdateView.as_view(), name='update_gram_stain'),

    path('zn-stain/create/<str:file_no>/', ZNStainCreateView.as_view(), name='create_zn_stain'),
    path('zn-stain/update/<str:file_no>/<int:test_info_pk>/', ZNStainUpdateView.as_view(), name='update_zn_stain'),

    path('semen-analysis/create/<str:file_no>/', SemenAnalysisCreateView.as_view(), name='create_semen_analysis'),
    path('semen-analysis/update/<str:file_no>/<int:test_info_pk>/', SemenAnalysisUpdateView.as_view(), name='update_semen_analysis'),

    path('urinalysis/create/<str:file_no>/', UrinalysisCreateView.as_view(), name='create_urinalysis'),
    path('urinalysis/update/<str:file_no>/<int:test_info_pk>/', UrinalysisUpdateView.as_view(), name='update_urinalysis'),

    path('pregnancy/create/<str:file_no>/', PregnancyCreateView.as_view(), name='create_pregnancy_test'),
    path('pregnancy/update/<str:file_no>/<int:test_info_pk>/', PregnancyUpdateView.as_view(), name='update_pregnancy_test'),

    path('pathology/lab-test/<str:file_no>/', LabTestingCreateView.as_view(), name='lab_test'),   
    path('get_lab/<str:lab_name>/', views.get_lab, name='get_lab'),
    path('test/<int:pk>/', LabTestDetailView.as_view(), name='test_detail'),
    path('test/pdf/<int:pk>/', TestPDFView.as_view(), name='test_pdf'),

    path('micro-req/list/',MicrobiologyTestListView.as_view(),name='micro_req'),
    path('chempath-req/list/',ChempathTestListView.as_view(),name='micro_req'),

    path('', include('django.contrib.auth.urls')),
]