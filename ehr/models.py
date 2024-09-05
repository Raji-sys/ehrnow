from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone
from django_quill.fields import QuillField
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


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


class Clinic(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)

    def get_absolute_url(self):
        return reverse('clinic_details', args=[self.name])

    def __str__(self):
        return f"{self.name}" if self.name else "unnamed"

class NursingDesk(models.Model):
    clinic = models.OneToOneField(Clinic, on_delete=models.CASCADE, related_name='nursing_desk')

    def get_absolute_url(self):
        return reverse('nursing_details', args=[self.clinic.pk])

    def __str__(self):
        return f"{self.clinic} nursing desk" if self.clinic else ""

class Room(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='consultation_rooms', null=True, blank=True)
    name = models.CharField(null=True, blank=True, max_length=200)

    def get_absolute_url(self):
        return reverse('room_details', args=[self.pk])

    def __str__(self):
        return f"{self.name}" if self.name else ""

@receiver(post_save, sender=Clinic)
def create_clinic_related_objects(sender, instance, created, **kwargs):
    if created:
        NursingDesk.objects.create(clinic=instance)
        for i in range(1, 5):
            Room.objects.create(clinic=instance, name=f"Room {i}")


class Ward(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)
    
    def get_absolute_url(self):
        return reverse('ward_details', args=[self.name])

    def __str__(self):
        if self.name:
            return f"{self.name}"

class Team(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)
    
    def get_absolute_url(self):
        return reverse('team_details', args=[self.name])

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

        
class PatientData(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    file_no = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    types = (('REGULAR', 'REGULAR'), ('NHIS', 'NHIS'),('RETAINER','RETAINER'))
    patient_type = models.CharField(choices=types, max_length=100, null=True, blank=True)
    titles = (('Mr.','Mr.'),('Mrs.','Mrs.'),('Miss','Miss'),('Alhaji','Alhaji'),('Mallam','Mallam'),('Chief','Chief'),('Prof.','Prof.'),('Dr.','Dr.'),('Engr.','Engr.'),('Ach.','Ach.'))
    title = models.CharField(choices=titles, max_length=10, null=True, blank=True)
    last_name = models.CharField('SURNAME', max_length=300, blank=True, null=True)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    other_name = models.CharField(max_length=300, blank=True, null=True)
    phone = models.CharField(max_length=11, null=True, blank=True, unique=True)
    # photo = models.ImageField(null=True, blank=True)
    sex = (('MALE', 'MALE'), ('FEMALE', 'FEMALE'))
    gender = models.CharField(choices=sex, max_length=10, null=True, blank=True)
    age=models.PositiveIntegerField(blank=True,null=True)
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
    clinic = models.ForeignKey(Clinic,on_delete=models.CASCADE, null=True,blank=True)
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
        if self.dob:
            today = date.today()
            self.age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        else:
            self.age = None

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

    def create_wallet(self):
        Wallet.objects.get_or_create(patient=self)


@receiver(post_save, sender=PatientData)
def create_patient_wallet(sender, instance, created, **kwargs):
    if created:
        instance.create_wallet()
    
class Services(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
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
    PAYMENT_METHODS = [
        ('CASH', 'CASH'),
        ('WALLET', 'WALLET'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='CASH',null=True,blank=True)
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.pk: 
            old_instance = Paypoint.objects.get(pk=self.pk)
            if not old_instance.status and self.status: 
                if self.payment_method == 'WALLET':
                    wallet = self.patient.wallet
                    try:
                        wallet.deduct_funds(self.price, self.service)  # Pass service as description
                    except ValidationError as e:
                        raise ValidationError(f"Wallet error: {str(e)}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.status}"


class FollowUpVisit(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE,related_name='follow_up')
    clinic = models.ForeignKey(Clinic,on_delete=models.CASCADE, null=True,blank=True)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    created = models.DateTimeField('date', auto_now_add=True)


class MedicalRecord(models.Model):
    services=(('new registration','new registration'),('follow up','follow up'),('card replacement','card replacement'))
    name = models.CharField(choices=services,max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = 'medical record'


class PatientHandover(models.Model):
    STATUS = [
        ('waiting for payment', 'Waiting for Payment'),
        ('waiting for follow up payment', 'Waiting for Follow Up Payment'),
        ('waiting for clinic assignment', 'Waiting for Clinic Assignment'),
        ('waiting for vital signs', 'Waiting for Vital Signs'),
        ('waiting for consultation', 'Waiting for Consultation'),
        ('seen', 'Seen'),
        ('awaiting review', 'Awaiting Review'),
    ]
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='handovers')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)
    nursing_desk = models.ForeignKey(NursingDesk, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=30, null=True, choices=STATUS)
    updated = models.DateField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Handover for {self.patient.file_no} in {self.clinic} - {self.status}"

    def close_handover(self):
        self.is_active = False
        self.status = 'seen'
        self.save()

    def __str__(self):
        return f"Handover for {self.patient.file_no} in {self.clinic} with {self.room} room"

class Appointment(models.Model):
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='appointments')
    clinic = models.ForeignKey(Clinic,on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def str(self):
        f"Appointment for {self.patient.file_no} in {self.clinic} with {self.team} team"

class VitalSigns(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room,on_delete=models.CASCADE, null=True)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='vital_signs')
    clinic = models.ForeignKey(Clinic,on_delete=models.CASCADE, null=True)
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


class RadiologyTest(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
    

class RadiologyResult(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    test = models.ForeignKey(RadiologyTest, max_length=100, null=True, blank=True, on_delete=models.CASCADE, related_name="results")
    patient = models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE, related_name="radiology_results")
    dicom_file = models.FileField(upload_to='dicom_files/', null=True, blank=True)
    local_file_path = models.CharField(max_length=255, null=True, blank=True)    
    cleared = models.BooleanField(default=False)
    comments = models.CharField(max_length=200, null=True, blank=True)
    payment = models.ForeignKey(Paypoint, null=True, on_delete=models.CASCADE, related_name="radiology_result_payment")
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'radiology results'

    def __str__(self):
        return str(self.patient)


class Admission(models.Model):
    STATUS = [
        ('ADMIT', 'ADMIT'),
        ('RECEIVED', 'RECEIVED'),
        ('DISCHARGE', 'DISCHARGE'),
    ]
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE, related_name="admission_info")
    status = models.CharField(max_length=30, null=True, choices=STATUS, default='ADMIT')
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, null=True)
    bed_number = models.CharField(max_length=300, null=True, blank=True)
    expected_discharge_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    updated = models.DateTimeField(auto_now=True)

    def days_on_admission(self):
        if self.created and self.status == 'RECEIVED':
            today = date.today()
            days_on = (today - self.created.date()).days
            return max(days_on, 0)  # Ensure non-negative value
        return 0

    def __str__(self):
        return f"{self.patient} - {self.status}"


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
    doctor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='ward_clinical_notes')
    note=QuillField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'ward notes'
    
    def __str__(self):
        return self.patient


class WardShiftSUmmaryNote(models.Model):
    nurse = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    note=QuillField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'ward shift summary notes'
    
    def __str__(self):
        return self.nurse

class Theatre(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('theatre_details', args=[self.name])

    def __str__(self):
        return self.name
    

class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='surgery_bill',null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Surgery Billing"


class TheatreItemCategory(models.Model):
    name=models.CharField(max_length=200,null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'theatre item categories'

    def __str__(self):
        return f"{self.name}"
    
class TheatreItem(models.Model):
    category = models.ForeignKey(TheatreItemCategory, on_delete=models.CASCADE,null=True,blank=True)
    name=models.CharField(max_length=200,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

class Billing(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items',null=True)
    category = models.ForeignKey(TheatreItemCategory, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(TheatreItem, on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1,null=True)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE,related_name="bill_payment")
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.name} (x{self.quantity})"

    @property
    def total_item_price(self):
        return self.item.price * self.quantity
       

class Physio(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE,related_name="physio_payment")
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.patient
    

class PrivateBill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='private_bill',null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Private Surgery Billing"

    
class PrivateTheatreItem(models.Model):
    name=models.CharField(max_length=200,null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    
class PrivateBilling(models.Model):
    private_bill = models.ForeignKey(PrivateBill, on_delete=models.CASCADE, related_name='private_items',null=True)
    item = models.ForeignKey(PrivateTheatreItem, on_delete=models.CASCADE,null=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE,related_name="private_bill_payment")
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.name}"
    

class Wallet(models.Model):
    patient = models.OneToOneField('PatientData', on_delete=models.CASCADE, related_name='wallet')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def balance(self):
        credits = self.transactions.filter(transaction_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or 0
        debits = self.transactions.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or 0
        return credits - debits

    def add_funds(self, amount):
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        WalletTransaction.objects.create(wallet=self, amount=amount, transaction_type='CREDIT')

    def deduct_funds(self, amount, description):
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        if self.balance() < amount:
            raise ValidationError("Insufficient funds")
        WalletTransaction.objects.create(wallet=self, amount=amount, transaction_type='DEBIT', description=description)

    def __str__(self):
        return f"{self.patient}"

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} for {self.wallet.patient}"
    

class TheatreBooking(models.Model):
    doctor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='theatre_bookings')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
    theatre = models.ForeignKey(Theatre, null=True, on_delete=models.CASCADE)
    diagnosis=models.CharField(max_length=200,null=True,blank=True)
    operation_planned=models.CharField(max_length=200,null=True,blank=True)
    date = models.DateField(null=True)
    blood_requirement=models.CharField(max_length=200,null=True,blank=True)
    note=QuillField(null=True, blank=True)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.patient

class MedicalIllness(models.Model):
    name=models.CharField(max_length=100,null=True)
    def __str__(self):
        return self.name

class PastSurgicalHistory(models.Model):
    surgery=models.CharField(max_length=100,null=True)
    when=models.CharField(max_length=100,null=True)
    where=models.CharField(max_length=100,null=True)
    LA_GA=models.CharField('L.A/G.A',max_length=100,null=True)
    outcome=models.CharField(max_length=100,null=True)
    def __str__(self):
        return self.surgery

class DrugHistory(models.Model):
    present_medication=models.CharField(max_length=100,null=True)
    allergies=models.CharField(max_length=100,null=True)
    def __str__(self):
        return f"{self.present_medication} {self.allergies}"

class SocialHistory(models.Model):
    item=models.CharField(max_length=100,null=True)
    qty=models.CharField(max_length=100,null=True)
    duration=models.CharField(max_length=100,null=True)

    def __str__(self):
        return f"{self.item} {self.qty} {self.duration}"

class LastMeal(models.Model):
    when=models.CharField(max_length=100,null=True)
    type=models.CharField(max_length=100,null=True)
    qty=models.CharField(max_length=100,null=True)

    def __str__(self):
        return f"{self.when} {self.type} {self.qty}"
        
class AnaesthisiaChecklist(models.Model):
    doctor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name="anaesthesia_checklist")
    concurrent_medical_illness=models.ManyToManyField(MedicalIllness,blank=True)
    past_medical_history=models.TextField(null=True)
    past_surgical_history=models.ForeignKey(PastSurgicalHistory,on_delete=models.CASCADE,null=True)
    options=(('YES','YES'),('NO','NO'))
    transfussion=models.CharField(choices=options,null=True, max_length=100)
    drug_history=models.ForeignKey(DrugHistory,on_delete=models.CASCADE,null=True)
    social_history=models.ForeignKey(SocialHistory,on_delete=models.CASCADE,null=True)
    denctures=models.CharField(choices=options,null=True, max_length=100)
    permanent=models.CharField(choices=options,null=True, max_length=100)
    temporary=models.CharField(choices=options,null=True, max_length=100)
    loose_teeth=models.CharField(choices=options,null=True, max_length=100)
    last_meal=models.ForeignKey(LastMeal,on_delete=models.CASCADE,null=True)
    comment=models.TextField(null=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.patient
    

class OperationNotes(models.Model):
    doctor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name="operation_notes")
    operated=models.BooleanField(default=False)
    notes=QuillField(null=True,blank=True)
    anaesthesia=(('GENERAL ANAESTHESIA','GENERAL ANAESTHESIA'),('SPINE ANAESTHESIA','SPINE ANAESTHESIA'))
    type_of_anaesthesia=models.CharField(choices=anaesthesia, max_length=300,null=True,blank=True)
    findings=models.CharField(max_length=300,null=True,blank=True)
    post_op_order=models.CharField('post-op order',max_length=300,null=True,blank=True)
    prescription=QuillField(null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural='operation notes'
    def __str__(self):
        return self.patient


class Consumable(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Implant(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class TheatreOperationRecord(models.Model):
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='theatre_operation_record')
    theatre = models.ForeignKey(Theatre, null=True, on_delete=models.CASCADE)
    ward = models.ForeignKey(Ward, null=True, on_delete=models.CASCADE)
    # ward = models.CharField(max_length=50,null=True,blank=True)
    
    # Operation Details
    diagnosis = models.CharField(max_length=200,null=True,blank=True)
    operation = models.CharField(max_length=200,null=True,blank=True)
    date_of_operation = models.DateField(null=True,blank=True)
    operation_suite = models.CharField(max_length=50,null=True,blank=True)
    
    # Staff
    surgeon = models.CharField(max_length=100,null=True,blank=True)
    assistant_1 = models.CharField(max_length=100, null=True,blank=True)
    assistant_2 = models.CharField(max_length=100, null=True,blank=True)
    assistant_3 = models.CharField(max_length=100, null=True,blank=True)
    instrument_nurse = models.CharField(max_length=100,null=True,blank=True)
    circulating_nurse = models.CharField(max_length=100,null=True,blank=True)
    anaesthetist = models.CharField(max_length=100,null=True,blank=True)
    
    consumables = models.ManyToManyField(Consumable, through='ConsumableUsage',blank=True)
    implants = models.ManyToManyField(Implant, through='ImplantUsage',blank=True)

    
    # Instrument Count
    towel_clips = models.IntegerField(default=0,null=True,blank=True)
    plain_gauze_small = models.IntegerField(default=0,null=True,blank=True)
    artery_forceps = models.IntegerField(default=0,null=True,blank=True)
    needles = models.IntegerField(default=0,null=True,blank=True)
    large_swabs = models.IntegerField(default=0,null=True,blank=True)
    
    # Tourniquet
    tourniquet_applied = models.BooleanField(default=False)
    tourniquet_time = models.TimeField(null=True, blank=True)
    tourniquet_by = models.CharField(max_length=100, blank=True)
    tourniquet_off_by = models.CharField(max_length=100, blank=True)
    tourniquet_off_time = models.TimeField(null=True, blank=True)
    
    comments = models.TextField(blank=True,null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} - {self.operation}"


class ConsumableUsage(models.Model):
    surgical_record = models.ForeignKey(TheatreOperationRecord, on_delete=models.CASCADE)
    consumable = models.ForeignKey(Consumable, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class ImplantUsage(models.Model):
    surgical_record = models.ForeignKey(TheatreOperationRecord, on_delete=models.CASCADE)
    implant = models.ForeignKey(Implant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

import os

class Archive(models.Model):
    patient = models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE, related_name='patient_archive')
    title = models.CharField(max_length=255,null=True)
    file = models.FileField(upload_to='patient_files/',validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],null=True)
    updated = models.DateTimeField(auto_now=True,null=True)

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = os.path.splitext(os.path.basename(self.file.name))[0]
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title