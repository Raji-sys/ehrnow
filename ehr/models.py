from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone
from django_quill.fields import QuillField
# from pathology.models import HematologyResult
from django.core.exceptions import ValidationError


class SerialNumberField(models.CharField):
    description = "A unique serial number field with leading zeros"

    def __init__(self, *args, **kwargs):
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["unique"]
        return name, path, args, kwargs
    

class Department(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)
    
    def get_absolute_url(self):
        return reverse('department_details', args=[self.name])

    def __str__(self):
        if self.name:
            return f"{self.name}"

class Unit(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, blank=True, max_length=300, null=True, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, blank=True, max_length=300, null=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=300, null=True, blank=True, unique=True)
    photo = models.ImageField(null=True, blank=True)
    sex = (('MALE', 'MALE'), ('FEMALE', 'FEMALE'))
    gender = models.CharField(choices=sex, max_length=10, null=True, blank=True)
    dob = models.DateField('date of birth', null=True, blank=True)
    created = models.DateTimeField('date added', auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('profile_details', args=[self.user.username])
    
    def full_name(self):
        return f"{self.user.get_full_name()}"

    def __str__(self):
        if self.user:
            return f"{self.full_name()}"


class Team(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)
    
    def get_absolute_url(self):
        return reverse('team_details', args=[self.name])

    def __str__(self):
        if self.name:
            return f"{self.name}"
        
    
class PatientData(models.Model):
    file_no = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    titles = (('Mr.','Mr.'),('Mrs.','Mrs.'),('Miss','Miss'),('Alhaji','Alhaji'),('Mallam','Mallam'),('Chief','Chief'),('Prof.','Prof.'),('Dr.','Dr.'),('Engr.','Engr.'),('Ach.','Ach.'))
    title = models.CharField(choices=titles, max_length=10, null=True, blank=True)
    last_name = models.CharField('SURNAME', max_length=300, blank=True, null=True)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    other_name = models.CharField(max_length=300, blank=True, null=True)
    phone = models.CharField(max_length=11, null=True, blank=True, unique=True)
    # photo = models.ImageField(null=True, blank=True)
    sex = (('MALE', 'MALE'), ('FEMALE', 'FEMALE'))
    gender = models.CharField(choices=sex, max_length=10, null=True, blank=True)
    dob = models.DateField('date of birth', null=True, blank=True)
    m_status = (('MARRIED', 'MARRIED'), ('SINGLE', 'SINGLE'), ('DIVORCED', 'DIVORCED'),('DIVORCEE', 'DIVORCEE'), ('WIDOW', 'WIDOW'), ('WIDOWER', 'WIDOWER'))
    marital_status = models.CharField(choices=m_status, max_length=100, null=True, blank=True)
    ns = (('NIGERIAN', 'NIGERIAN'), ('NON-CITIZEN', 'NON-CITIZEN'))
    nationality = models.CharField(choices=ns, max_length=200, null=True, blank=True)
    geo_political_zone = (('NORTH-EAST', 'NORTH-EAST'), ('NORTH-WEST', 'NORTH-WEST'), ('NORTH-CENTRAL', 'NORTH-CENTRAL'),('SOUTH-EAST', 'SOUTH-EAST'), ('SOUTH-WEST', 'SOUTH-WEST'), ('SOUTH-SOUTH', 'SOUTH-SOUTH'))
    zone = models.CharField(blank=True, choices=geo_political_zone, max_length=300, null=True)
    state = models.CharField(blank=True, max_length=300, null=True)
    lga = models.CharField(blank=True, max_length=300, null=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    faith = (('ISLAM', 'ISLAM'), ('CHRISTIANITY', 'CHRISTIANITY'),('TRADITIONAL', 'TRADITIONAL'))
    religion = models.CharField(choices=faith, max_length=100, null=True, blank=True)
    tribes = (('HAUSA', 'Hausa'),
        ('IGBO', 'Igbo'),
        ('IBIRA', 'Ibira'),
        ('FULANI', 'Fulani'),
        ('KANURI', 'Kanuri'),
        ('IJAW', 'Ijaw'),
        ('TIV', 'Tiv'),
        ('NUPE', 'Nupe'),
        ('EFIK', 'Efik'),
        ('IDOMA', 'Idoma'),
        ('IBIBIO', 'Ibibio'),
        ('IGALA', 'Igala'),
        ('ANNANG', 'Annang'),
        ('EBIRA', 'Ebira'),
        ('JUKUN', 'Jukun'),
        ('BINI', 'Bini'),
        ('GWARi', 'Gwari'),
        ('KURAMA', 'Kurama'),
        ('ANGAS', 'Angas'),
        ('BACHAMA', 'Bachama'),
        ('MBULA', 'Mbula'),
        ('KAGORO', 'Kagoro'),
        ('KAMUKU', 'Kamuku'),
        ('TAROK', 'Tarok'),
        ('BIROM', 'Birom'),
        ('BURA', 'Bura'),
        ('MARGI', 'Margi'),
        ('SHUA', 'Shua'),
        ('AWORI', 'Awori'),
        ('EKITI', 'Ekiti'),
        ('IJEBU', 'Ijebu'),
        ('IKALE', 'Ikale'),
        ('ILORIN', 'Ilorin'),
        ('ONDO', 'Ondo'),
        ('OSHOGBO', 'Oshogbo'),
        ('OYO', 'Oyo'),
        ('YAGBA', 'Yagba'),
        ('KABBA', 'Kabba'),
        ('Other','other'))
    tribe = models.CharField(choices=tribes, max_length=100, null=True, blank=True)
    occupation = models.CharField(max_length=300, null=True, blank=True)
    role_in_occupation = models.CharField(max_length=300, null=True, blank=True)
    nok_name = models.CharField('next of kin name', max_length=300, null=True, blank=True)
    nok_phone = models.CharField('next of kin phone', max_length=300, null=True, blank=True)
    nok_addr = models.CharField('next of kin address', max_length=300, null=True, blank=True)
    rel = (('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'),('SON', 'SON'),('DAUGHTER','DAUGHTER'),('BROTHER','BROTHER'),('SISTER','SISTER'),
           ('UNCLE','UNCLE'),('AUNT','AUNT'),('NEPHEW','NEPHEW'),('NIECE','NIECE'),('GRANDFATHER','GRANDFATHER'),('GRANDMOTHER','GRANDMOTHTER'),
           ('GRANDSON','GRANDSON'),('GRANDDAUGHTER','GRANDAUGHTER'),('COUSIN','COUSIN'),('OTHER','OTHER'))
    nok_rel = models.CharField('relationship with next of kin',choices=rel, max_length=300, null=True, blank=True)
    # nok_photo = models.ImageField('first next of kin photo', null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'patients data'
    
    def save(self, *args, **kwargs):
        if not self.file_no:
            last_instance = self.__class__.objects.order_by('file_no').last()

            if last_instance:
                last_file_no = int(last_instance.file_no)
                new_file_no = f"{last_file_no + 1:06d}"  # 06 for 6 leading zeros
            else:
                new_file_no = "000001"

            self.file_no = new_file_no

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('patient_details', args=[self.file_no])

    def full_name(self):
        name_parts=[
            self.title or "",
            self.first_name or "",
            self.last_name or "",
            self.other_name or "",
        ]
        return " ".join(filter(None,name_parts))
    
    def __str__(self):
        return self.full_name()
    
        
    def age(self):
        today = date.today()
        if self.dob:
            age = today.year - self.dob.year
            if today.month < self.dob.month or (today.month == self.dob.month and today.day < self.dob.day):
                age -= 1
            return age

    # def is_birthday(self):
    #     today = date.today()
    #     if self.dob:
    #         return today.month == self.dob.month and today.day == self.dob.day
    #     return False

class Room(models.Model):
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),]    
    ROOM_CHOICES = [
        ('ROOM 1', 'ROOM 1'),
        ('ROOM 2', 'ROOM 2'),
        ('ROOM 3', 'ROOM 3')
    ]
    # patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=30, null=True, choices=ROOM_CHOICES)
    clinic = models.CharField(max_length=30, null=True, choices=CLINIC_CHOICES)
    waiting_since = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    class Meta:
        verbose_name_plural = 'virtual room'
    
    def get_absolute_url(self):
        return reverse('room_details', args=[self.pk])

    def __str__(self):
        return self.name


class Services(models.Model):
    type=models.CharField(max_length=100, null=True, blank=True)
    name=models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type}----{self.name}"

    class Meta:
        verbose_name_plural = 'general services'

class Paypoint(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name="patient_payments")
    service = models.CharField(max_length=100, null=True, blank=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    status=models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateField(auto_now=True)
   

class FollowUpVisit(models.Model):
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
    ]

    patient=models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE,related_name='follow_up')
    clinic = models.CharField(max_length=30, null=True, choices=CLINIC_CHOICES)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    created = models.DateTimeField('date', auto_now_add=True)


class MedicalRecord(models.Model):
    services=(('new registration','new registration'),('follow up','follow up'),('card replacement','card replacement'))
    name = models.CharField(choices=services,max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE,related_name='medical_record_payment',blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = 'medical record'


class PatientHandover(models.Model):
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
    ]

    ROOM_CHOICES = [
        ('ROOM 1', 'ROOM 1'),
        ('ROOM 2', 'ROOM 2'),
        ('ROOM 3', 'ROOM 3')
    ]
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='handovers')
    clinic = models.CharField(max_length=30, null=True, choices=CLINIC_CHOICES)
    room = models.CharField(max_length=30, null=True, choices=ROOM_CHOICES)
    status = models.CharField(max_length=30, null=True, choices=[
        ('waiting_for_payment', 'Waiting for Payment'),
        ('waiting_for_clinic_assignment', 'Waiting for Clinic Assignment'),
        ('waiting_for_vital_signs', 'Waiting for Vital Signs'),
        ('waiting_for_consultation', 'Waiting for Consultation'),
        ('complete','complete'),
        ('await_review','await review'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def str(self):
        f"Handover for {self.patient.file_no} in {self.clinic} with {self.room} room"

class Appointment(models.Model):
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
    ]
    TEAM_CHOICES = [
        ('WHITE', 'WHITE'),
        ('GREEN', 'GREEN'),
        ('BLUE', 'BLUE'),
        ('YELLOW', 'YELLOW')
    ]

    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='appointments')
    clinic = models.CharField(max_length=30, null=True, choices=CLINIC_CHOICES)
    team = models.CharField(max_length=30, null=True, choices=TEAM_CHOICES)
    date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def str(self):
        f"Appointment for {self.patient.file_no} in {self.clinic} with {self.team} team"

class VitalSigns(models.Model):
    ROOM_CHOICES = [
        ('ROOM 1', 'ROOM 1'),
        ('ROOM 2', 'ROOM 2'),
        ('ROOM 3', 'ROOM 3')
    ]
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
    ]
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    room = models.CharField(max_length=30, null=True, choices=ROOM_CHOICES)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='vital_signs')
    clinic = models.CharField(max_length=30, null=True, choices=CLINIC_CHOICES)
    body_temperature=models.CharField(max_length=10, null=True, blank=True)
    pulse_rate=models.CharField(max_length=10, null=True, blank=True)
    respiration_rate=models.CharField(max_length=10, null=True, blank=True)
    blood_pressure=models.CharField(max_length=10, null=True, blank=True)
    blood_oxygen=models.CharField(max_length=10, null=True, blank=True)
    blood_glucose=models.CharField(max_length=10, null=True, blank=True)
    weight=models.CharField(max_length=10, null=True, blank=True)
    height=models.CharField(max_length=10, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def str(self):
        f"Vitals for {self.patient.file_no} in {self.clinic} with {self.room} room"

    class Meta:
        verbose_name_plural = 'vital signs'

class ClinicalNote(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='clinical_notes')
    note=QuillField(null=True, blank=True)
    diagnosis=models.CharField(max_length=200,null=True,blank=True)
    needs_review = models.BooleanField(default=False)    
    appointment=models.CharField(max_length=200,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('clincal_note_details', args=[self.user])

    def __str__(self):
        return f"notes for: {self.patient.file_no}"

class DicomFile(models.Model):
    file = models.FileField(upload_to='dicom_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class RadiologyTest(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
    
class RadiologyResult(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    test = models.ForeignKey(RadiologyTest, max_length=100, null=True, blank=True, on_delete=models.CASCADE,related_name="results")
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name="radiology_result")
    dicom_file = models.FileField(upload_to='dicom_files/')
    cleared=models.BooleanField(default=False)
    comments=models.CharField(max_length=200,null=True, blank=True)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'radiology results'

    def __str__(self):
        return self.patient
    

class Admission(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name="admission_info")
    # payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    admit=models.BooleanField(default=False)
    accept=models.BooleanField(default=False)
    wards=(('MALE WARD','MALE WARD'),('FEMALE WARD','FEMALE WARD'),('CHILDRENS WARD','CHILDRENS WARD'),('ICU','ICU'))
    ward=models.CharField(choices=wards,max_length=300,null=True, blank=True)
    # room=models.CharField(max_length=300,null=True, blank=True)
    bed_number=models.CharField(max_length=300,null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.patient.full_name().upper()


class WardVitalSigns(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='ward_vital_signs')
    body_temperature=models.CharField(max_length=10, null=True, blank=True)
    pulse_rate=models.CharField(max_length=10, null=True, blank=True)
    respiration_rate=models.CharField(max_length=10, null=True, blank=True)
    blood_pressure=models.CharField(max_length=10, null=True, blank=True)
    blood_oxygen=models.CharField(max_length=10, null=True, blank=True)
    blood_glucose=models.CharField(max_length=10, null=True, blank=True)
    weight=models.CharField(max_length=10, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'ward vital signs'

    def __str__(self):
        return self.patient

class WardMedication(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='ward_medication')
    drug=models.CharField(max_length=10, null=True, blank=True)
    dose=models.CharField(max_length=10, null=True, blank=True)
    comments=models.CharField(max_length=10, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'ward vital signs'

    def __str__(self):
        return self.patient


class WardClinicalNote(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='ward_clinical_notes')
    note=QuillField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'ward notes'
    
    def __str__(self):
        return self.patient

class TheatreBooking(models.Model):
    THEATRES = [
        ('MAIN THEATRE', 'MAIN THEATRE'),
        ('SPINE THEATRE', 'SPINE THEATRE'),
    ]
    TEAMS = [
        ('WHITE', 'WHITE'),
        ('GREEN', 'GREEN'),
        ('BLUE', 'BLUE'),
        ('YELLOW', 'YELLOW')
    ]
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='theatre_bookings')
    theatre = models.CharField(max_length=30, null=True, choices=THEATRES)
    team = models.CharField(max_length=30, null=True, choices=TEAMS)
    date = models.DateField(null=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.patient


class TheatreNotes(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name="theatre_notes")
    operated=models.BooleanField(default=False)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    operation_notes=QuillField(null=True,blank=True)
    anaesthesia=(('GENERAL ANAESTHESIA','GENERAL ANAESTHESIA'),('SPINE ANAESTHESIA','SPINE ANAESTHESIA'))
    type_of_anaesthesia=models.CharField(choices=anaesthesia, max_length=300,null=True,blank=True)
    findings=models.CharField(max_length=300,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.patient


class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='surgery_bill',null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True)

    def __str__(self):
        return f"Bill for {self.patient}"


class TheatreItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items',null=True)
    name = models.CharField(max_length=100,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    quantity = models.PositiveIntegerField(default=1,null=True)

    def __str__(self):
        return f"{self.name} (x{self.quantity})"

    @property
    def total_item_price(self):
        return self.price * self.quantity

class CartItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(TheatreItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_item_price(self):
        return self.item.price * self.quantity
        
class Physio(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.patient



# class NHIS(models.Model):
#     user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
#     patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
#     payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
#     created = models.DateTimeField('transaction date', auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)

#     def get_absolute_url(self):
#         return reverse('pay_details', args=[self.user])

#     def full_name(self):
#         return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

#     def __str__(self):
#         if self.user:
#             return f"{self.full_name}"


# class PandO(models.Model):
#     user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
#     patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
#     payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
#     updated = models.DateTimeField(auto_now=True)

#     def get_absolute_url(self):
#         return reverse('pay_details', args=[self.user])

#     def full_name(self):
#         return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

#     def __str__(self):
#         if self.user:
#             return f"{self.full_name}"


# class Audit(models.Model):
#     user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
#     patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
#     updated = models.DateTimeField(auto_now=True)

#     def get_absolute_url(self):
#         return reverse('pay_details', args=[self.user])

#     def full_name(self):
#         return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

#     def __str__(self):
#         if self.user:
#             return f"{self.full_name}"
