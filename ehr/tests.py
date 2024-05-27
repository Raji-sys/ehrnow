# tests/test_models.py

from django.test import TestCase
from django.utils import timezone
from datetime import date
from .models import *
from django.urls import reverse
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse


# class PatientDataModelTest(TestCase):

#     def setUp(self):
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             other_name='Middle',
#             phone='12345678901',
#             gender='MALE',
#             dob=date(1990, 1, 1),
#             marital_status='SINGLE',
#             nationality='NIGERIAN',
#             zone='NORTH-WEST',
#             state='Kaduna',
#             lga='Kaduna South',
#             address='1234 Elm Street',
#             religion='CHRISTIANITY',
#             tribe='IGBO',
#             occupation='Engineer',
#             role_in_occupation='Senior Engineer',
#             nok_name='Jane Doe',
#             nok_phone='09876543210',
#             nok_addr='5678 Oak Street',
#             nok_rel='SISTER'
#         )

#     def test_file_no_auto_generation(self):
#         self.assertTrue(self.patient.file_no)
#         self.assertEqual(len(self.patient.file_no), 7)
#         self.assertEqual(self.patient.file_no, '0000001')

#     def test_full_name(self):
#         expected_full_name = 'Mr. Doe John Middle'
#         self.assertEqual(self.patient.full_name(), expected_full_name)

#     def test_get_absolute_url(self):
#         expected_url = f'/record/patient/{self.patient.file_no}/'
#         self.assertEqual(self.patient.get_absolute_url(), expected_url)

#     def test_age(self):
#         today = date.today()
#         expected_age = today.year - 1990
#         if today.month < 1 or (today.month == 1 and today.day < 1):
#             expected_age -= 1
#         self.assertEqual(self.patient.age(), expected_age)

#     def test_string_representation(self):
#         expected_str = 'Mr. Doe John Middle'
#         self.assertEqual(str(self.patient), expected_str)

# # tests/test_models.py


# class ServicesModelTest(TestCase):

#     def setUp(self):
#         self.service = Services.objects.create(
#             type='Consultation',
#             name='General Consultation',
#             price=50.00
#         )

#     def test_string_representation(self):
#         expected_str = 'Consultation----General Consultation'
#         self.assertEqual(str(self.service), expected_str)


# class PaypointModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.paypoint = Paypoint.objects.create(
#             user=self.user,
#             patient=self.patient,
#             service='Consultation',
#             price=50.00,
#             status=False
#         )

#     def test_string_representation(self):
#         expected_str = 'Consultation'
#         self.assertEqual(str(self.paypoint.service), expected_str)

# class FollowUpVisitModelTest(TestCase):

#     def setUp(self):
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.paypoint = Paypoint.objects.create(
#             user=None,
#             patient=self.patient,
#             service='Consultation',
#             price=50.00,
#             status=False
#         )
#         self.follow_up_visit = FollowUpVisit.objects.create(
#             patient=self.patient,
#             clinic='SOPD',
#             payment=self.paypoint
#         )

#     def test_string_representation(self):
#         expected_str = 'FollowUpVisit object (1)'
#         self.assertEqual(str(self.follow_up_visit), expected_str)


# class MedicalRecordModelTest(TestCase):

#     def setUp(self):
#         self.paypoint = Paypoint.objects.create(
#             user=None,
#             patient=None,
#             service='new registration',
#             price=20.00,
#             status=True
#         )
#         self.medical_record = MedicalRecord.objects.create(
#             name='new registration',
#             price=20.00,
#             payment=self.paypoint
#         )

#     def test_string_representation(self):
#         expected_str = 'new registration'
#         self.assertEqual(str(self.medical_record), expected_str)

#     def test_verbose_name_plural(self):
#         self.assertEqual(str(MedicalRecord._meta.verbose_name_plural), 'medical record')


# class PatientHandoverModelTest(TestCase):

#     def setUp(self):
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.handover = PatientHandover.objects.create(
#             patient=self.patient,
#             clinic='SOPD',
#             room='ROOM 1',
#             status='waiting_for_payment'
#         )


# class AppointmentModelTest(TestCase):

#     def setUp(self):
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.appointment = Appointment.objects.create(
#             patient=self.patient,
#             clinic='SOPD',
#             team='WHITE',
#             date=date.today()
#         )


# class VitalSignsModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.vital_signs = VitalSigns.objects.create(
#             user=self.user,
#             patient=self.patient,
#             clinic='SOPD',
#             room='ROOM 1',
#             body_temperature='36.6',
#             pulse_rate='70',
#             respiration_rate='18',
#             blood_pressure='120/80',
#             blood_oxygen='98',
#             blood_glucose='5.5',
#             weight='70',
#             height='175'
#         )


#     def test_verbose_name_plural(self):
#         self.assertEqual(str(VitalSigns._meta.verbose_name_plural), 'vital signs')


# class ClinicalNoteModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.clinical_note = ClinicalNote.objects.create(
#             user=self.user,
#             patient=self.patient,
#             note='Test note',
#             diagnosis='Test diagnosis',
#             needs_review=False,
#             appointment='Test appointment'
#         )

# # tests/test_models.py

# from django.test import TestCase
# from django.contrib.auth.models import User
# from datetime import date
# from .models import PatientData, Paypoint, Radiology, Admission, WardVitalSigns, WardMedication, WardClinicalNote, TheatreBooking, TheatreNotes

# class RadiologyModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.paypoint = Paypoint.objects.create(
#             user=self.user,
#             patient=self.patient,
#             service='Radiology Service',
#             price=100.00,
#             status=False
#         )
#         self.radiology = Radiology.objects.create(
#             user=self.user,
#             patient=self.patient,
#             dicom_file='path/to/dicom/file.dcm',
#             payment=self.paypoint
#         )

#     def test_instance_creation(self):
#         self.assertIsInstance(self.radiology, Radiology)
#         self.assertEqual(self.radiology.patient, self.patient)


# class AdmissionModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.admission = Admission.objects.create(
#             user=self.user,
#             patient=self.patient,
#             admit=True,
#             accept=True,
#             ward='MALE WARD',
#             bed_number='A1'
#         )

#     def test_instance_creation(self):
#         self.assertIsInstance(self.admission, Admission)
#         self.assertEqual(self.admission.patient, self.patient)


# class WardVitalSignsModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.vital_signs = WardVitalSigns.objects.create(
#             user=self.user,
#             patient=self.patient,
#             body_temperature='36.6',
#             pulse_rate='70',
#             respiration_rate='18',
#             blood_pressure='120/80',
#             blood_oxygen='98',
#             blood_glucose='5.5',
#             weight='70'
#         )

#     def test_instance_creation(self):
#         self.assertIsInstance(self.vital_signs, WardVitalSigns)
#         self.assertEqual(self.vital_signs.patient, self.patient)


# class WardMedicationModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.medication = WardMedication.objects.create(
#             user=self.user,
#             patient=self.patient,
#             drug='Aspirin',
#             dose='100mg',
#             comments='Take with food'
#         )

#     def test_instance_creation(self):
#         self.assertIsInstance(self.medication, WardMedication)
#         self.assertEqual(self.medication.patient, self.patient)


# class WardClinicalNoteModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.clinical_note = WardClinicalNote.objects.create(
#             user=self.user,
#             patient=self.patient,

#         )

#     def test_instance_creation(self):
#         self.assertIsInstance(self.clinical_note, WardClinicalNote)
#         self.assertEqual(self.clinical_note.patient, self.patient)


# class TheatreBookingModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.booking = TheatreBooking.objects.create(
#             user=self.user,
#             patient=self.patient,
#             theatre='MAIN THEATRE',
#             team='WHITE',
#             date=date.today()
#         )

#     def test_instance_creation(self):
#         self.assertIsInstance(self.booking, TheatreBooking)
#         self.assertEqual(self.booking.patient, self.patient)


# class TheatreNotesModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.paypoint = Paypoint.objects.create(
#             user=self.user,
#             patient=self.patient,
#             service='Surgery',
#             price=200.00,
#             status=False
#         )
#         self.theatre_note = TheatreNotes.objects.create(
#             user=self.user,
#             patient=self.patient,
#             operated=True,
#             payment=self.paypoint,
#             operation_notes='Operation successful.',
#             type_of_anaesthesia='GENERAL ANAESTHESIA',
#             findings='No complications.'
#         )

#     def test_instance_creation(self):
#         self.assertIsInstance(self.theatre_note, TheatreNotes)
#         self.assertEqual(self.theatre_note.patient, self.patient)


# from django.test import TestCase, Client
# from django.contrib.auth.models import User, Permission, Group
# from django.urls import reverse
# from ehr.models import PatientData, PatientHandover

# class PatientCreateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
        
#         # Add necessary permissions to the user
#         add_permission = Permission.objects.get(codename='add_patientdata')
#         self.user.user_permissions.add(add_permission)

#         # Ensure user is part of the 'record' group
#         record_group, created = Group.objects.get_or_create(name='record')
#         self.user.groups.add(record_group)

#         self.client.login(username='testuser', password='12345')
#         self.url = reverse('new_patient')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/record/new_patient.html')

#     def test_post_request(self):
#         data = {
#             'title': 'Mr.',
#             'last_name': 'Doe',
#             'first_name': 'John',
#             'phone': '12345678901'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('medical_record'))
#         self.assertTrue(PatientData.objects.filter(first_name='John').exists())
#         self.assertTrue(PatientHandover.objects.filter(patient__first_name='John', clinic='A & E').exists())




# class UpdatePatientViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.client.login(username='testuser', password='12345')
#         self.url = reverse('update_patient', args=[self.patient.pk])

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/record/update_patient.html')

#     def test_post_request(self):
#         data = {
#             'title': 'Mr.',
#             'last_name': 'DoeUpdated',
#             'first_name': 'John',
#             'phone': '12345678901'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.patient.refresh_from_db()
#         self.assertEqual(self.patient.last_name, 'DoeUpdated')

# class PatientListViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('patient_list')
#         self.patient1 = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.patient2 = PatientData.objects.create(
#             title='Mrs.',
#             last_name='Smith',
#             first_name='Jane',
#             phone='9876543210'
#         )

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/record/patient_list.html')
#         self.assertIn('patients', response.context)
#         self.assertIn(self.patient1, response.context['patients'])
#         self.assertIn(self.patient2, response.context['patients'])
#         self.assertIn('patientFilter', response.context)
#         self.assertIn('total_patient', response.context)
#         self.assertEqual(response.context['total_patient'], 2)

# class PatientReportViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('patient_report')
#         self.patient1 = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.patient2 = PatientData.objects.create(
#             title='Mrs.',
#             last_name='Smith',
#             first_name='Jane',
#             phone='9876543210'
#         )

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/report/patient_report.html')
#         self.assertIn('patients', response.context)
#         self.assertIn(self.patient1, response.context['patients'])
#         self.assertIn(self.patient2, response.context['patients'])
#         self.assertIn('patientReportFilter', response.context)
#         self.assertIn('total_patient', response.context)
#         self.assertEqual(response.context['total_patient'], 2)


# # tests/test_views.py
# 
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from ehr.models import PatientData, PatientHandover, FollowUpVisit
from django.core.exceptions import PermissionDenied

# class PatientStatsViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.client.login(username='testuser', password='12345')
#         self.url = reverse('patient_stats')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/record/stats.html')
#         self.assertIn('pc', response.context)
#         self.assertIn('gender_counts', response.context)
#         self.assertIn('geo_counts', response.context)
#         self.assertIn('state_counts', response.context)
#         self.assertIn('lga_counts', response.context)
#         self.assertIn('religion_counts', response.context)
#         self.assertIn('marital_status_counts', response.context)
#         self.assertIn('nationality_counts', response.context)
#         self.assertIn('occupation_counts', response.context)
#         self.assertIn('role_in_occupation_counts', response.context)
#         self.assertIn('address_counts', response.context)


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from ehr.models import PatientData, FollowUpVisit, PatientHandover
from django.core.exceptions import PermissionDenied

class PatientFolderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.patient = PatientData.objects.create(
            title='Mr.',
            last_name='Doe',
            first_name='John',
            phone='12345678901'
        )
        self.url = reverse('patient_details', args=[self.patient.file_no])

    def test_get_request_with_permission(self):
        doctor_group = Group.objects.create(name='doctor')
        self.user.groups.add(doctor_group)
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ehr/record/patient_folder.html')

    def test_get_request_without_permission(self):
        self.client.login(username='testuser', password='12345')
        with self.assertRaises(PermissionDenied):
            self.client.get(self.url)

from django.contrib.auth.models import Group, Permission

# class FollowUpVisitCreateViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.',
#             last_name='Doe',
#             first_name='John',
#             phone='12345678901'
#         )
#         self.url = reverse('follow_up', kwargs={'file_no': self.patient.file_no})

#         # Add the required permissions or group to the test user
#         # required_permission = Permission.objects.get(name='record')
#         # self.user.user_permissions.add(required_permission)
#         # OR
#         record_group, _ = Group.objects.get_or_create(name='record')

#     # Add the test user to the 'record' group
#         self.user.groups.add(record_group)
#         self.client.login(username='testuser', password='12345')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/record/follow_up.html')

#     def test_post_request(self):
#         data = {
#             'clinic': 'SOPD',
#             'date': '2024-05-01'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('medical_record'))
#         self.assertTrue(FollowUpVisit.objects.filter(patient=self.patient, clinic='SOPD').exists())
#         self.assertTrue(PatientHandover.objects.filter(patient=self.patient, clinic='SOPD').exists())

# tests/test_views.py

# from django.test import TestCase, Client
# from django.urls import reverse
# from django.contrib.auth.models import User, Group
# from ehr.models import PatientHandover, PatientData, FollowUpVisit, Paypoint, MedicalRecord
# from ehr.forms import PayForm
# from django.shortcuts import get_object_or_404
# from django.contrib.messages import get_messages

# class PaypointDashboardViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.url = reverse('paypoint_dashboard')
#         self.group = Group.objects.create(name='revenue')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')
#         self.handover = PatientHandover.objects.create(
#             patient=PatientData.objects.create(
#                 title='Mr.', last_name='Doe', first_name='John', phone='12345678901'
#             ),
#             clinic='A & E',
#             status='waiting_for_payment'
#         )

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/revenue/paypoint_dash.html')
#         self.assertIn('handovers', response.context)
#         self.assertEqual(len(response.context['handovers']), 1)


# class PaypointFollowUpDashboardViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.url = reverse('paypoint_follow_up_dashboard')
#         self.group = Group.objects.create(name='revenue')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.', last_name='Doe', first_name='John', phone='12345678901'
#         )
#         self.handover = PatientHandover.objects.create(
#             patient=self.patient, clinic='A & E', status='waiting_for_payment'
#         )
#         self.visit = FollowUpVisit.objects.create(
#             patient=self.patient, clinic='A & E'
#         )

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/revenue/follow_up_pay_dash.html')
#         self.assertIn('handovers', response.context)
#         self.assertEqual(len(response.context['handovers']), 1)


# class PaypointViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.url = reverse('paypoint', args=['123456'])
#         self.group = Group.objects.create(name='revenue')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.', last_name='Doe', first_name='John', phone='12345678901', file_no='123456'
#         )
#         self.handover = PatientHandover.objects.create(
#             patient=self.patient, clinic='A & E', status='waiting_for_payment'
#         )
#         self.service = MedicalRecord.objects.create(name='new registration', price=100)

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/revenue/paypoint.html')
#         self.assertIn('patient', response.context)
#         self.assertIn('handover', response.context)
#         self.assertIn('service', response.context)

#     def test_post_request(self):
#         data = {
#             'service': 'new registration',
#             'price': 100
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('revenue'))
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'Payment successful. Patient handed over for vital signs.')
#         self.handover.refresh_from_db()
#         self.assertEqual(self.handover.status, 'waiting_for_vital_signs')
#         self.assertTrue(Paypoint.objects.filter(patient=self.patient, service='new registration', price=100).exists())


# class PaypointFollowUpViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.url = reverse('paypoint_follow_up', args=['123456'])
#         self.group = Group.objects.create(name='revenue')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.', last_name='Doe', first_name='John', phone='12345678901', file_no='123456'
#         )
#         self.handover = PatientHandover.objects.create(
#             patient=self.patient, clinic='A & E', status='waiting_for_payment'
#         )
#         self.service = MedicalRecord.objects.create(name='follow up', price=50)

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/revenue/paypoint_follow_up.html')
#         self.assertIn('patient', response.context)
#         self.assertEqual(response.context['service_name'], 'follow up')
#         self.assertEqual(response.context['service_price'], 50)

#     def test_post_request(self):
#         data = {
#             'service': 'follow up',
#             'price': 50
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('revenue'))
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'Payment successful. Patient handed over for vitals.')
#         self.handover.refresh_from_db()
#         self.assertEqual(self.handover.status, 'waiting_for_vital_signs')
#         self.assertTrue(Paypoint.objects.filter(patient=self.patient, service='follow up', price=50).exists())

# # tests/test_views.py

# from django.test import TestCase, Client
# from django.urls import reverse
# from django.utils import timezone
# from django.contrib.auth.models import User, Group
# from ehr.models import PatientHandover, PatientData, VitalSigns, ClinicalNote, FollowUpVisit, Paypoint, MedicalRecord
# from ehr.forms import VitalSignsForm, ClinicalNoteForm, ClinicalNoteUpdateForm
# from datetime import timedelta
# from django.contrib.messages import get_messages

# class VitalSignCreateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testnurse', password='12345')
#         self.url = reverse('vital_signs_create', args=['123456'])
#         self.group = Group.objects.create(name='nurse')
#         self.user.groups.add(self.group)
#         self.client.login(username='testnurse', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.', last_name='Doe', first_name='John', phone='12345678901', file_no='123456'
#         )

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/nurse/vital_signs.html')
#         self.assertIn('patient', response.context)

#     def test_post_request(self):
#         data = {
#             'blood_pressure': '120/80',
#             'temperature': '36.6',
#             'pulse': '70',
#             'respiration': '20',
#             'handover_room': 'ROOM 1'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('nursing'))
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'Vitals taken, Patient handed over for consultation')
#         handover = PatientHandover.objects.get(patient=self.patient)
#         self.assertEqual(handover.status, 'waiting_for_consultation')
#         self.assertEqual(handover.room, 'ROOM 1')
#         self.assertTrue(VitalSigns.objects.filter(patient=self.patient).exists())


# class ClinicalNoteCreateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testdoctor', password='12345')
#         self.url = reverse('clinical_note_create', args=['123456'])
#         self.group = Group.objects.create(name='doctor')
#         self.user.groups.add(self.group)
#         self.client.login(username='testdoctor', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.', last_name='Doe', first_name='John', phone='12345678901', file_no='123456'
#         )

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/doctor/clinical_note.html')
#         self.assertIn('patient', response.context)

#     def test_post_request(self):
#         data = {
#             'note': 'Patient has a cold.',
#             'needs_review': True
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'PATIENT SEEN.')
#         handover = PatientHandover.objects.get(patient=self.patient)
#         self.assertEqual(handover.status, 'await review')
#         self.assertTrue(ClinicalNote.objects.filter(patient=self.patient).exists())


# class ClinicalNoteUpdateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testdoctor', password='12345')
#         self.url = reverse('clinical_note_update', args=[1])
#         self.group = Group.objects.create(name='doctor')
#         self.user.groups.add(self.group)
#         self.client.login(username='testdoctor', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.', last_name='Doe', first_name='John', phone='12345678901', file_no='123456'
#         )
#         self.clinical_note = ClinicalNote.objects.create(
#             patient=self.patient, note='Patient has a cold.', needs_review=True
#         )

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/doctor/update_clinical_note.html')
#         self.assertIn('form', response.context)

#     def test_post_request(self):
#         data = {
#             'note': 'Patient has a cold. Updated.',
#             'needs_review': False
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'CLINICAL NOTE UPDATED')
#         self.clinical_note.refresh_from_db()
#         self.assertEqual(self.clinical_note.note, 'Patient has a cold. Updated.')


# class ClinicListViewTests(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testdoctor', password='12345')
#         self.group = Group.objects.create(name='doctor')
#         self.user.groups.add(self.group)
#         self.client.login(username='testdoctor', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.', last_name='Doe', first_name='John', phone='12345678901', file_no='123456'
#         )
#         self.handover = PatientHandover.objects.create(
#             patient=self.patient, clinic='A & E', status='waiting_for_vital_signs'
#         )

#     def test_ae_nursing_desk_view(self):
#         url = reverse('ae_nursing_desk')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/nurse/ae_nursing_desk.html')
#         self.assertIn('handovers', response.context)

#     def test_sopd_nursing_desk_view(self):
#         url = reverse('sopd_nursing_desk')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/nurse/sopd_nursing_desk.html')
#         self.assertIn('handovers', response.context)

#     def test_ae_consultation_wait_room_view(self):
#         url = reverse('ae_consultation_wait_room')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/clinic/ae_list.html')
#         self.assertIn('handovers', response.context)

#     def test_ae_room1_view(self):
#         url = reverse('ae_room1')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/clinic/ae_room1.html')
#         self.assertIn('handovers', response.context)

#     def test_ae_room2_view(self):
#         url = reverse('ae_room2')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/clinic/ae_room2.html')
#         self.assertIn('handovers', response.context)

#     def test_sopd_consultation_wait_room_view(self):
#         url = reverse('sopd_consultation_wait_room')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/clinic/sopd_list.html')
#         self.assertIn('handovers', response.context)

#     def test_sopd_room1_view(self):
#         url = reverse('sopd_room1')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/clinic/sopd_room1.html')
#         self.assertIn('handovers', response.context)

#     def test_sopd_room2_view(self):
#         url = reverse('sopd_room2')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/clinic/sopd_room2.html')
#         self.assertIn('handovers', response.context)

#     def test_ae_consultation_finish_view(self):
#         self.handover.status = 'complete'
#         self.handover.save()
#         url = reverse('ae_consultation_finish')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/doctor/ae_patient_seen.html')
#         self.assertIn('handovers', response.context)

#     def test_ae_awaiting_review_view(self):
#         self.handover.status = 'await review'
#         self.handover.save()
#         url = reverse('ae_awaiting_review')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/doctor/ae_review_patient.html')
#         self.assertIn('handovers', response.context)

#     def test_sopd_consultation_finish_view(self):
#         self.handover.clinic = 'SOPD'
#         self.handover.status = 'complete'
#         self.handover.save()
#         url = reverse('sopd_consultation_finish')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/doctor/sopd_patient_seen.html')
#         self.assertIn('handovers', response.context)

#     def test_sopd_awaiting_review_view(self):
#         self.handover.clinic = 'SOPD'
#         self.handover.status = 'await review'
#         self.handover.save()
#         url = reverse('sopd_awaiting_review')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/doctor/sopd_review_patient.html')
#         self.assertIn('handovers', response.context)

# # tests/test_views.py

# from django.test import TestCase, Client
# from django.urls import reverse
# from django.contrib.auth.models import User, Group
# from ehr.models import PatientData, Appointment
# from ehr.forms import AppointmentForm
# from datetime import datetime
# from django.contrib.messages import get_messages


# class AppointmentCreateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testrecord', password='12345')
#         self.url = reverse('appointment_create', args=['123456'])
#         self.group = Group.objects.create(name='record')
#         self.user.groups.add(self.group)
#         self.client.login(username='testrecord', password='12345')
#         self.patient = PatientData.objects.create(
#             title='Mr.', last_name='Doe', first_name='John', phone='12345678901', file_no='123456'
#         )

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/record/new_appointment.html')
#         self.assertIn('form', response.context)

#     def test_post_request(self):
#         data = {
#             'date': datetime.now().date(),
#             'time': datetime.now().time(),
#             'notes': 'Follow-up appointment'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('patient_list'))
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'APPOINTMENT ADDED')
#         self.assertTrue(Appointment.objects.filter(patient=self.patient).exists())


# class AppointmentUpdateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testrecord', password='12345')
#         self.appointment = Appointment.objects.create(
#             date=datetime.now().date(),
#             time=datetime.now().time(),
#             notes='Follow-up appointment'
#         )
#         self.url = reverse('appointment_update', args=[self.appointment.pk])
#         self.group = Group.objects.create(name='record')
#         self.user.groups.add(self.group)
#         self.client.login(username='testrecord', password='12345')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/record/update_appt.html')
#         self.assertIn('form', response.context)

#     def test_post_request(self):
#         data = {
#             'date': datetime.now().date(),
#             'time': datetime.now().time(),
#             'notes': 'Follow-up appointment updated'
#         }
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('appointments'))
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'Appointment Updated Successfully')
#         self.appointment.refresh_from_db()
#         self.assertEqual(self.appointment.notes, 'Follow-up appointment updated')


# class NewAppointmentListViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testrecord', password='12345')
#         self.url = reverse('new_appointment_list')
#         self.group = Group.objects.create(name='record')
#         self.user.groups.add(self.group)
#         self.client.login(username='testrecord', password='12345')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/record/new_appt_list.html')
#         self.assertIn('patientFilter', response.context)


# class AppointmentListViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testrecord', password='12345')
#         self.url = reverse('appointment_list')
#         self.group = Group.objects.create(name='record')
#         self.user.groups.add(self.group)
#         self.client.login(username='testrecord', password='12345')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/record/appointment.html')
#         self.assertIn('appointmentFilter', response.context)

# # tests/test_views.py

# from django.test import TestCase, Client
# from django.urls import reverse
# from django.contrib.auth.models import User, Group
# from ehr.models import MedicalRecord,  Services, Paypoint
# from pathology.models import *
# from django.contrib.messages import get_messages
# from datetime import datetime


# class HospitalServicesListViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('hospital_services')
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.group = Group.objects.create(name='record')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')
#         MedicalRecord.objects.create(name='Record 1')
#         HematologyTest.objects.create(name='Hematology 1')
#         Services.objects.create(name='Service 1')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/dashboard/services.html')
#         self.assertIn('medical_record', response.context)
#         self.assertIn('hematology', response.context)
#         self.assertIn('services', response.context)


# class ServiceCreateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('service_create')
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.group = Group.objects.create(name='record')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/revenue/new_service.html')
#         self.assertIn('form', response.context)

#     def test_post_request(self):
#         data = {'name': 'New Service', 'description': 'A new service', 'price': 100}
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('hospital_services'))
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'SERVICE ADDED')
#         self.assertTrue(Services.objects.filter(name='New Service').exists())


# class ServiceUpdateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.service = Services.objects.create(name='Service 1')
#         self.url = reverse('service_update', args=[self.service.pk])
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.group = Group.objects.create(name='record')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/revenue/update_service.html')
#         self.assertIn('form', response.context)

#     def test_post_request(self):
#         data = {'name': 'Service 1 Updated', 'description': 'An updated service', 'price': 150}
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('service_list'))
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'Service Updated Successfully')
#         self.service.refresh_from_db()
#         self.assertEqual(self.service.name, 'Service 1 Updated')


# class ServiceListViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('service_list')
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.group = Group.objects.create(name='record')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')
#         Services.objects.create(name='Service 1')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/revenue/general_services.html')
#         self.assertIn('serviceFilter', response.context)
#         self.assertIn('total_services', response.context)


# class PayCreateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('pay_create')
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.group = Group.objects.create(name='revenue')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/revenue/new_pay.html')
#         self.assertIn('form', response.context)

#     def test_post_request(self):
#         data = {'amount': 100}
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('pay_list'))
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'PAYMENT ADDED')
#         self.assertTrue(Paypoint.objects.filter(amount=100).exists())


# class PayUpdateViewTest(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.paypoint = Paypoint.objects.create(amount=100)
#         self.url = reverse('pay_update', args=[self.paypoint.pk])
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.group = Group.objects.create(name='revenue')
#         self.user.groups.add(self.group)
#         self.client.login(username='testuser', password='12345')

#     def test_get_request(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/revenue/update_pay.html')
#         self.assertIn('form', response.context)
#         self.assertEqual(response.context['patient'], self.paypoint.patient)
#         self.assertEqual(response.context['service'], self.paypoint.service)

#     def test_post_request(self):
#         data = {'amount': 150}
#         response = self.client.post(self.url, data)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('pay_list'))
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(str(messages[0]), 'PAYMENT ADDED')
#         self.assertTrue(Paypoint.objects.filter(amount=100).exists())

# from django.test import TestCase, Client
# from django.urls import reverse
# from django.contrib.auth.models import User
# from ehr.models import Admission, PatientData
# from ehr.forms import AdmissionForm, AdmissionUpdateForm
# from ehr.filters import AdmissionFilter

# class AdmissionCreateViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.patient = PatientData.objects.create(file_no='123')

#     def test_admission_create_view(self):
#         url = reverse('admission_create', kwargs={'file_no': self.patient.file_no})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/ward/new_admission.html')

#     def test_admission_form_valid(self):
#         form_data = {'ward': 'ICU', 'admit_reason': 'Test reason'}
#         form = AdmissionForm(data=form_data)
#         self.assertTrue(form.is_valid())

#         url = reverse('admission_create', kwargs={'file_no': self.patient.file_no})
#         response = self.client.post(url, data=form_data)
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(Admission.objects.count(), 1)

# class AdmissionUpdateViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.patient = PatientData.objects.create(file_no='123')
#         self.admission = Admission.objects.create(patient=self.patient, user=self.user)

#     def test_admission_update_view(self):
#         url = reverse('admission_update', kwargs={'pk': self.admission.pk})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/ward/update_admission.html')

#     def test_admission_form_valid(self):
#         form_data = {'ward': 'MALE WARD', 'admit_reason': 'Updated reason'}
#         form = AdmissionUpdateForm(data=form_data, instance=self.admission)
#         self.assertTrue(form.is_valid())

#         url = reverse('admission_update', kwargs={'pk': self.admission.pk})
#         response = self.client.post(url, data=form_data)
#         self.assertEqual(response.status_code, 302)
#         self.admission.refresh_from_db()
#         self.assertEqual(self.admission.ward, 'MALE WARD')
#         self.assertEqual(self.admission.admit_reason, 'Updated reason')

# class AdmissionListViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.patient = PatientData.objects.create(file_no='123')
#         self.admission = Admission.objects.create(patient=self.patient, user=self.user)

#     def test_admission_list_view(self):
#         url = reverse('admission_list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/ward/admission_list.html')
#         self.assertContains(response, self.admission.patient.file_no)

#     def test_admission_filter(self):
#         url = reverse('admission_list') + '?ward=ICU'
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.context['admissions']), 0)

#         self.admission.ward = 'ICU'
#         self.admission.save()

#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.context['admissions']), 1)

# from django.test import TestCase, Client
# from django.urls import reverse
# from django.contrib.auth.models import User
# from ehr.models import Admission, PatientData, WardVitalSigns, WardMedication, WardClinicalNote, TheatreBooking, TheatreNotes
# from ehr.forms import WardVitalSignsForm, WardMedicationForm, WardNotesForm, TheatreBookingForm, TheatreNotesForm

# class ChildrensWardViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.patient = PatientData.objects.create(file_no='123')
#         self.admission = Admission.objects.create(patient=self.patient, user=self.user, ward='CHILDRENS WARD')

#     def test_childrens_ward_wait_list_view(self):
#         url = reverse('childrens_ward_wait_list')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/ward/childrens_ward_wait_list.html')
#         self.assertContains(response, self.patient.file_no)

#     def test_childrens_ward_view(self):
#         self.admission.accept = True
#         self.admission.save()
#         url = reverse('childrens_ward')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/ward/childrens_ward.html')
#         self.assertContains(response, self.patient.file_no)

# class WardVitalSignCreateViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.patient = PatientData.objects.create(file_no='123')

#     def test_ward_vital_sign_create_view(self):
#         url = reverse('ward_vital_signs', kwargs={'file_no': self.patient.file_no})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/ward/ward_vital_signs.html')

#     def test_ward_vital_sign_form_valid(self):
#         form_data = {'temperature': 36.5, 'pulse': 80, 'respiration_rate': 18, 'blood_pressure': '120/80'}
#         form = WardVitalSignsForm(data=form_data)
#         self.assertTrue(form.is_valid())

#         url = reverse('ward_vital_signs', kwargs={'file_no': self.patient.file_no})
#         response = self.client.post(url, data=form_data)
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(WardVitalSigns.objects.count(), 1)

# # Add tests for other ward-related views (WardMedicationCreateView, WardNotesCreateView) as needed

# class TheatreBookingCreateViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.patient = PatientData.objects.create(file_no='123')

#     def test_theatre_booking_create_view(self):
#         url = reverse('theatre_booking', kwargs={'file_no': self.patient.file_no})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/theatre/book_theatre.html')

#     def test_theatre_booking_form_valid(self):
#         form_data = {'surgery_date': '2023-06-01', 'surgery_time': '10:00', 'surgery_type': 'Appendectomy'}
#         form = TheatreBookingForm(data=form_data)
#         self.assertTrue(form.is_valid())

#         url = reverse('theatre_booking', kwargs={'file_no': self.patient.file_no})
#         response = self.client.post(url, data=form_data)
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(TheatreBooking.objects.count(), 1)

# class TheatreBookingUpdateViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.patient = PatientData.objects.create(file_no='123')
#         self.booking = TheatreBooking.objects.create(patient=self.patient, user=self.user)

#     def test_theatre_booking_update_view(self):
#         url = reverse('update_theatre_booking', kwargs={'pk': self.booking.pk})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/theatre/update_theatre_booking.html')

#     def test_theatre_booking_form_valid(self):
#         form_data = {'surgery_date': '2023-06-02', 'surgery_time': '14:00', 'surgery_type': 'Cholecystectomy'}
#         form = TheatreBookingForm(data=form_data, instance=self.booking)
#         self.assertTrue(form.is_valid())

#         url = reverse('update_theatre_booking', kwargs={'pk': self.booking.pk})
#         response = self.client.post(url, data=form_data)
#         self.assertEqual(response.status_code, 302)
#         self.booking.refresh_from_db()
#         self.assertEqual(self.booking.surgery_date.strftime('%Y-%m-%d'), '2023-06-02')
#         self.assertEqual(self.booking.surgery_time.strftime('%H:%M'), '14:00')
#         self.assertEqual(self.booking.surgery_type, 'Cholecystectomy')


# class TheatreBookingListViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.patient = PatientData.objects.create(file_no='123')
#         self.booking = TheatreBooking.objects.create(patient=self.patient, user=self.user)

#     def test_theatre_booking_list_view(self):
#         url = reverse('theatre_bookings')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'ehr/theatre/theatre_bookings.html')
#         self.assertContains(response, self.patient.file_no)


# class TheatreNotesCreateViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')
#         self.patient = PatientData.objects.create(file_no='123')

    # def test_theatre_notes_create_view(self):
    #     url = reverse('theatre_notes', kwargs={'file_no': self.patient.file_no})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200