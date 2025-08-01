from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
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
import os


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

# @receiver(post_save, sender=Clinic)
# def create_clinic_related_objects(sender, instance, created, **kwargs):
#     if created:
#         NursingDesk.objects.create(clinic=instance)
#         for i in range(1, 5):
#             Room.objects.create(clinic=instance, name=f"Room {i}")

@receiver(post_save, sender=Clinic)
def create_clinic_related_objects(sender, instance, created, **kwargs):
    if created:
        from pharm.models import Unit  # Import here instead
        
        NursingDesk.objects.create(clinic=instance)
        Unit.objects.create(clinic=instance, name=instance.name)
        for i in range(1, 5):
            Room.objects.create(clinic=instance, name=f"Room {i}")


class Ward(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)

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
    # photo = models.ImageField(null=True, blank=True)
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
    types_of_id = (('NIN', 'NIN'), ('Voters Card', 'Voters Card'),('Drivers Liscence','Drivers Liscence'),('International Passport','International Passport'))
    means_of_id = models.CharField('Means of Identification',choices=types_of_id, max_length=200, null=True, blank=True)
    id_number = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    file_no = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    titles = (('Mr.','Mr.'),('Mrs.','Mrs.'),('Miss','Miss'),('Alhaji','Alhaji'),('Mallam','Mallam'),('Chief','Chief'),('Prof.','Prof.'),('Dr.','Dr.'),('Engr.','Engr.'),('Ach.','Ach.'))
    title = models.CharField(choices=titles, max_length=10, null=True, blank=True)
    last_name = models.CharField('SURNAME', max_length=300, null=True)
    first_name = models.CharField(max_length=300, null=True)
    other_name = models.CharField(max_length=300, null=True, blank=True)
    phone = models.CharField(max_length=22, null=True, unique=True)
    # photo = models.ImageField(null=True, blank=True)
    sex = (('MALE', 'MALE'), ('FEMALE', 'FEMALE'),('FAMILY', 'FAMILY'))
    gender = models.CharField(choices=sex, max_length=10, null=True)
    age=models.PositiveIntegerField(null=True)
    dob = models.DateField('date of birth', null=True, blank=True)
    m_status = (('MARRIED', 'MARRIED'), ('SINGLE', 'SINGLE'), ('DIVORCED', 'DIVORCED'),('DIVORCEE', 'DIVORCEE'), ('WIDOW', 'WIDOW'), ('WIDOWER', 'WIDOWER'))
    marital_status = models.CharField(choices=m_status, max_length=100, null=True, blank=True)
    ns = (('NIGERIAN', 'NIGERIAN'), ('NON-CITIZEN', 'NON-CITIZEN'))
    nationality = models.CharField(choices=ns, max_length=200, null=True,blank=True)
    geo_political_zone = (('NORTH-EAST', 'NORTH-EAST'), ('NORTH-WEST', 'NORTH-WEST'), ('NORTH-CENTRAL', 'NORTH-CENTRAL'),('SOUTH-EAST', 'SOUTH-EAST'), ('SOUTH-WEST', 'SOUTH-WEST'), ('SOUTH-SOUTH', 'SOUTH-SOUTH'))
    zone = models.CharField( choices=geo_political_zone, max_length=300, null=True, blank=True)
    state = models.CharField(max_length=300, null=True, blank=True)
    lga = models.CharField(max_length=300, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    faith = (('ISLAM', 'ISLAM'), ('CHRISTIANITY', 'CHRISTIANITY'),('TRADITIONAL', 'TRADITIONAL'),('OTHER','OTHER'))
    religion = models.CharField(choices=faith, max_length=100, null=True,blank=True)
    tribes = (('HAUSA', 'Hausa'),
        ('YORUBA','Yoruba'),
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
        ('GWARI', 'Gwari'),
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
    nok_name = models.CharField('name', max_length=300, null=True, blank=True)
    nok_phone = models.CharField('phone', max_length=22, null=True, unique=True, blank=True)
    rel = (('SPOUSE','SPOUSE'),('FATHER', 'FATHER'), ('MOTHER', 'MOTHER'),('SON', 'SON'),('DAUGHTER','DAUGHTER'),('BROTHER','BROTHER'),('SISTER','SISTER'),
           ('UNCLE','UNCLE'),('AUNT','AUNT'),('NEPHEW','NEPHEW'),('NIECE','NIECE'),('GRANDFATHER','GRANDFATHER'),('GRANDMOTHER','GRANDMOTHTER'),
           ('GRANDSON','GRANDSON'),('GRANDDAUGHTER','GRANDAUGHTER'),('COUSIN','COUSIN'),('FRIEND','FRIEND'),('OTHER','OTHER'))
    nok_rel = models.CharField('relationship',choices=rel, max_length=300, null=True, blank=True)
    nok_addr_options = (('SAME', 'SAME'), ('DIFFERENT ADDRESS', 'DIFFERENT ADDRESS'))
    nok_addr = models.CharField('address',choices=nok_addr_options, max_length=300, null=True, blank=True)
    nok_addr_if = models.CharField('address if different', max_length=300, null=True, blank=True)
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
        if self.dob:
            today = date.today()
            self.age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        else:
            self.age = None

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('patient_details', args=[self.file_no])
    
    def full_name(self):
        try:
            name_parts = [
                str(self.title or '').strip(),
                str(self.first_name or '').strip(),
                str(self.last_name or '').strip(),
                str(self.other_name or '').strip()
            ]
            return " ".join(filter(None, name_parts)) or f"Patient {self.file_no}"
        except Exception as e:
            return f"Patient {self.file_no}"

    def __str__(self):
        return str(self.full_name())

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
    description =QuillField(null=True, blank=True)
    
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type}--{self.name}--{self.price}"

    class Meta:
        verbose_name_plural = 'general services'

class Paypoint(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name="patient_payments")
    service = models.CharField(max_length=300, null=True, blank=True)  
    unit = models.CharField(max_length=100, null=True, blank=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    status=models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    PAYMENT_METHODS = [
        ('CASH', 'CASH'),
        ('WALLET', 'WALLET'),
        ('CREDIT','CREDIT'),
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

    class Meta:
        indexes = [
            models.Index(fields=['patient', 'unit', 'status', 'created']),
        ]

class MedicalRecord(models.Model):
    services=(('new registration','new registration'),('follow up','follow up'),('review','review'),('dressing','dressing'),('card replacement','card replacement'))
    name = models.CharField(choices=services,max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = 'medical record'

class VisitRecord(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    record = models.ForeignKey(MedicalRecord, max_length=100, null=True, blank=False, on_delete=models.CASCADE, related_name="visits")
    clinic = models.ForeignKey(Clinic,on_delete=models.CASCADE, null=True,blank=False)    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
    patient = models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE, related_name="visit_record")
    payment = models.ForeignKey(Paypoint, null=True, on_delete=models.CASCADE, related_name="record_payment")
    nursing_desk = models.ForeignKey(NursingDesk, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    vitals=models.BooleanField(default=False)
    consultation=models.BooleanField(default=False)
    seen=models.BooleanField(default=False)
    review=models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateField(auto_now=True)

    def get_status_display(self):
        if self.review and not self.seen:
            return "review (direct to doctor)"
        elif not self.vitals and not self.review:
            return "Waiting for nurse"
        elif self.vitals and not self.seen and not self.review:
            return "Waiting for doctor"
        elif self.seen and not self.review:
            return "Seen"
        elif self.seen and self.review:
            return "Review"
        else:
            return "Completed"
    def close_visit(self):
        self.consultation = False
        self.seen = True
        self.review = False
        self.save()

    def __str__(self):
        return f"{self.patient}"

    class Meta:
        verbose_name_plural = 'visit record'


# class Appointment(models.Model):
#     user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
#     patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='appointments')
#     clinic = models.ForeignKey(Clinic,on_delete=models.CASCADE, null=True)
#     team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
#     date = models.DateField(null=True)
#     time = models.TimeField(null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
    
#     def str(self):
#         f"Appointment for {self.patient.file_no} in {self.clinic} with {self.team} team"
# BONUS: Enhanced model method for more detailed conflict information
class Appointment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='appointments')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(null=True)  
    time = models.TimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Appointment for {self.patient.file_no} in {self.clinic} with {self.team} team"

    class Meta:
        ordering = ['-date', '-time']
        
    def has_conflicts(self):
        """Check if this appointment conflicts with existing appointments"""
        conflicting_appointments = Appointment.objects.filter(
            date=self.date,
            time=self.time,
            clinic=self.clinic
        )
        
        # Exclude self if this is an existing appointment (for updates)
        if self.pk:
            conflicting_appointments = conflicting_appointments.exclude(pk=self.pk)
            
        return conflicting_appointments.exists()
    
    def get_conflicting_appointments(self):
        """Get the actual conflicting appointment objects"""
        conflicting_appointments = Appointment.objects.filter(
            date=self.date,
            time=self.time,
            clinic=self.clinic
        )
        
        if self.pk:
            conflicting_appointments = conflicting_appointments.exclude(pk=self.pk)
            
        return conflicting_appointments
    
    def get_conflict_details(self):
        """Get detailed information about conflicts"""
        conflicts = self.get_conflicting_appointments()
        if conflicts.exists():
            return {
                'has_conflicts': True,
                'conflict_count': conflicts.count(),
                'conflicting_patients': [appt.patient.file_no for appt in conflicts],
                'conflicting_appointments': conflicts
            }
        return {'has_conflicts': False}
    
class VitalSigns(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room,on_delete=models.CASCADE, null=True)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='vital_signs')
    clinic = models.ForeignKey(Clinic,on_delete=models.CASCADE, null=True)
    body_temperature = models.CharField(max_length=10, null=True, blank=True, help_text="°C")
    pulse_rate = models.CharField(max_length=10, null=True, blank=True, help_text="bpm")
    respiration_rate = models.CharField(max_length=10, null=True, blank=True, help_text="breaths/min")
    blood_pressure = models.CharField(max_length=10, null=True, blank=True, help_text="mmHg")
    blood_oxygen = models.CharField(max_length=10, null=True, blank=True, help_text="%")
    blood_glucose = models.CharField(max_length=10, null=True, blank=True, help_text="mg/dL")
    weight = models.CharField(max_length=10, null=True, blank=True, help_text="kg")
    height = models.CharField(max_length=10, null=True, blank=True, help_text="cm")
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
    updated = models.DateTimeField(auto_now=True)
    # created_at= models.DateField(auto_now_add=True, null=True)
    def get_absolute_url(self):
        return reverse('clincal_note_details', args=[self.user])

    def __str__(self):
        return f"notes for: {self.patient.file_no}"

    def is_editable(self):
            """Check if the clinical note is still within the 30-minute edit window"""
            if not self.updated:
                return False
            
            time_since_creation = timezone.now() - self.updated
            edit_window = timedelta(minutes=30)
            return time_since_creation <= edit_window
        
    def minutes_remaining_for_edit(self):
        """Get remaining minutes for editing, returns 0 if window expired"""
        if not self.updated:
            return 0
        
        time_since_creation = timezone.now() - self.updated
        edit_window = timedelta(minutes=30)
        time_remaining = edit_window - time_since_creation
        
        if time_remaining.total_seconds() <= 0:
            return 0
        
        return int(time_remaining.total_seconds() // 60)

class RadiologyTest(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"
    

class Admission(models.Model):
    payment = models.ForeignKey(Paypoint, null=True, on_delete=models.CASCADE, related_name="admission_payment")
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
    notes = QuillField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def days_on_admission(self):
        if self.created and self.status == 'RECEIVED':
            today = date.today()
            days_on = (today - self.created.date()).days
            return max(days_on, 0)  # Ensure non-negative value
        return 0
    
    def calculate_total_cost(self):
        # Safely handle ward price being None or missing
        if not self.ward:
            return 0
            
        # Safely get ward price - default to 0 if None
        ward_price = getattr(self.ward, 'price', 0) or 0
        
        if self.expected_discharge_date:
            days = (self.expected_discharge_date - self.created.date()).days + 1
            days = max(days, 1)
            return ward_price * days
        
        # Handle case where expected_discharge_date is None
        if self.created:
            # Use days_on_admission instead
            days = self.days_on_admission() or 1
            return ward_price * days
        
        return 0
    
    def expected_days(self):
        if not self.expected_discharge_date or not self.created:
            return 0
            
        days = (self.expected_discharge_date - self.created.date()).days + 1
        return max(days, 0)  # Ensure non-negative value
    
    def __str__(self):
        patient_name = str(self.patient) if self.patient else "Unknown Patient"
        status = self.status or "Unknown Status"
        return f"{patient_name} - {status}"

class WardVitalSigns(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='ward_vital_signs')
    body_temperature = models.CharField(max_length=10, null=True, blank=True, help_text="°C")
    pulse_rate = models.CharField(max_length=10, null=True, blank=True, help_text="bpm")
    respiration_rate = models.CharField(max_length=10, null=True, blank=True, help_text="breaths/min")
    blood_pressure = models.CharField(max_length=10, null=True, blank=True, help_text="mmHg")
    blood_oxygen = models.CharField(max_length=10, null=True, blank=True, help_text="%")
    blood_glucose = models.CharField(max_length=10, null=True, blank=True, help_text="mg/dL")
    weight = models.CharField(max_length=10, null=True, blank=True, help_text="kg")
    height = models.CharField(max_length=10, null=True, blank=True, help_text="cm")
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'ward vital signs'

    def __str__(self):
        return self.patient
    
class WardMedication(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE, related_name='ward_medication')
    drug = models.CharField(max_length=200, null=True, blank=True)  # Keep as CharField!
    dose = models.CharField(max_length=10, null=True, blank=True)
    comments = models.CharField(max_length=200, null=True, blank=True)  # Increased length
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'ward medications'
    
    def __str__(self):
        return str(self.patient)

class PatientDispensedDrug(models.Model):
    """Track dispensed drugs for each patient"""
    patient = models.ForeignKey('PatientData', on_delete=models.CASCADE, related_name='dispensed_drugs_stock')
    drug_name = models.CharField(max_length=200)
    total_dispensed = models.PositiveIntegerField('Total Dispensed')
    remaining_quantity = models.PositiveIntegerField('Remaining Quantity')
    dispensed_date = models.DateTimeField()
    dispensed_by = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-dispensed_date']
        
    def __str__(self):
        return f"{self.drug_name} - {self.remaining_quantity} remaining"


class WardMedicationDispensed(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey('PatientData', null=True, on_delete=models.CASCADE, related_name='ward_medication_dispensed')
    dispensed_drug = models.ForeignKey(PatientDispensedDrug, on_delete=models.CASCADE, related_name='administrations')
    dose_administered = models.PositiveIntegerField('Qty Given')
    comments = models.CharField(max_length=200, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True)  # Changed to auto_now_add to prevent updates
    
    class Meta:
        verbose_name_plural = 'Ward Medications (Dispensed)'
        ordering = ['-updated']
    
    def save(self, *args, **kwargs):
        """Fixed save method to prevent double deduction"""
        with transaction.atomic():
            # Only process if this is a new record (not an update)
            if not self.pk:
                # Refresh the dispensed_drug object to get latest data
                self.dispensed_drug.refresh_from_db()
                
                # Validate quantity
                if self.dose_administered > self.dispensed_drug.remaining_quantity:
                    raise ValidationError(
                        f"Insufficient quantity. Only {self.dispensed_drug.remaining_quantity} units available for {self.dispensed_drug.drug_name}."
                    )
                
                # Deduct from remaining quantity
                self.dispensed_drug.remaining_quantity -= self.dose_administered
                self.dispensed_drug.save(update_fields=['remaining_quantity'])
            
            # Save the administration record
            super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.dispensed_drug.drug_name} - {self.dose_administered} administered to {self.patient}"


class WardClinicalNote(models.Model):
    doctor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='ward_clinical_notes')
    note=QuillField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'ward notes'
    
    def __str__(self):
        return self.patient


class WardShiftNote(models.Model):
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='ward_shift_notes')
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
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bill for:{self.patient}"


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

class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='surgery_bill',null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True)
    theatre_booking = models.ForeignKey(TheatreBooking, null=True, blank=True, on_delete=models.SET_NULL)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Surgery Bill"


class Billing(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items',null=True)
    category = models.ForeignKey(TheatreItemCategory, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(TheatreItem, on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1,null=True)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE,related_name="bill_payment")
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bill.patient.file_no} {self.item.name} (x{self.quantity})"

    @property
    def total_item_price(self):
        return self.item.price * self.quantity
           

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
    private_bill = models.ForeignKey(PrivateBill, on_delete=models.CASCADE, related_name='private_items', null=True)
    item = models.ForeignKey(PrivateTheatreItem, on_delete=models.CASCADE, null=True, blank=True)
    custom_item_name = models.CharField(max_length=200, null=True, blank=True, help_text="Enter custom item name if not in dropdown")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    payment = models.ForeignKey(Paypoint, null=True, on_delete=models.CASCADE, related_name="private_bill_payment")
    updated = models.DateTimeField(auto_now=True)

    def get_item_name(self):
        """Return the item name - either from the ForeignKey or custom field"""
        if self.custom_item_name:
            return self.custom_item_name
        elif self.item:
            return self.item.name
        return "Unknown Item"

    def __str__(self):
        return f"{self.get_item_name()}"

    class Meta:
        # Ensure either item or custom_item_name is provided, but not both
        constraints = [
            models.CheckConstraint(
                check=~(models.Q(item__isnull=False) & models.Q(custom_item_name__isnull=False)),
                name='only_one_item_type'
            )
        ]

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
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} for {self.wallet.patient}"
    

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
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural='operation notes'

    def __str__(self):
        return f"{self.patient}"


class AnaesthesiaChecklist(models.Model):
    doctor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, null=True, on_delete=models.CASCADE)
    ward = models.ForeignKey(Ward, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE, related_name="anaesthesia_checklist")
    transfussion = models.CharField(choices=[('YES', 'YES'), ('NO', 'NO')], null=True, max_length=100)
    denctures = models.CharField(choices=[('YES', 'YES'), ('NO', 'NO')], null=True, max_length=100)
    permanent = models.CharField(choices=[('YES', 'YES'), ('NO', 'NO')], null=True, max_length=100)
    temporary = models.CharField(choices=[('YES', 'YES'), ('NO', 'NO')], null=True, max_length=100)
    lose_teeth = models.CharField(choices=[('YES', 'YES'), ('NO', 'NO')], null=True, max_length=100)
    comment = QuillField(null=True, blank=True)
    past_medical_history = QuillField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('anaesthesia_checklist_details', args=[self.id])

    def __str__(self):
        return f"{self.patient}"

class ConcurrentMedicalIllness(models.Model):
    anaesthesia_checklist = models.ForeignKey(AnaesthesiaChecklist, null=True, on_delete=models.CASCADE, related_name="concurrent_medical_illnesses")
    illness = models.CharField(max_length=255,null=True,blank=True) 
    description = QuillField(null=True, blank=True)

    def __str__(self):
        return f"{self.anaesthesia_checklist.patient} - {self.illness}"


class PastSurgicalHistory(models.Model):
    anaesthesia_checklist = models.ForeignKey(AnaesthesiaChecklist, null=True, on_delete=models.CASCADE, related_name="past_surgical_history")
    surgery = models.CharField(max_length=255,null=True,blank=True)
    when = models.DateField(null=True,blank=True)
    where = models.CharField(max_length=255,null=True,blank=True)
    LA_GA = models.CharField(max_length=255,null=True,blank=True, choices=[('LA', 'Local Anaesthesia'), ('GA', 'General Anaesthesia')])
    outcome = QuillField(null=True, blank=True)

    def __str__(self):
        return f"{self.anaesthesia_checklist.patient} - {self.surgery}"

class DrugHistory(models.Model):
    anaesthesia_checklist = models.ForeignKey(AnaesthesiaChecklist, null=True, on_delete=models.CASCADE, related_name="drug_history")
    medication = models.CharField(max_length=255,null=True,blank=True)
    allergies = models.CharField(max_length=255,null=True,blank=True)
    is_present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.anaesthesia_checklist.patient} - {self.medication}"

class SocialHistory(models.Model):
    anaesthesia_checklist = models.ForeignKey(AnaesthesiaChecklist, null=True, on_delete=models.CASCADE, related_name="social_history")
    item = models.CharField(max_length=255,null=True,blank=True)
    quantity = models.IntegerField(null=True,blank=True)
    duration = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return f"{self.anaesthesia_checklist.patient} - {self.item}"

class LastMeal(models.Model):
    anaesthesia_checklist = models.ForeignKey(AnaesthesiaChecklist, null=True, on_delete=models.CASCADE, related_name="last_meals")
    when = models.DateTimeField(null=True,blank=True)
    meal_type = models.CharField(max_length=255,null=True,blank=True)
    quantity = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return f"{self.anaesthesia_checklist.patient} - {self.when}"

    
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
    
    comments = QuillField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('theatre_operation_record_details', args=[self.id])

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
    

class PhysioTest(models.Model):
    CATEGORY_CHOICES = [
        ("manual_muscle_strength", "Manual Muscle Strength Tests"),
        ("range_of_motion", "Range of Motion Tests"),
        ("orthopedic", "Orthopedic Tests"),
        ("neurological", "Neurological Tests"),
        ("functional_capacity", "Functional Capacity Tests"),
        ("pain_assessment", "Pain Assessment Tests"),
        ("special_condition", "Special Condition Tests"),
        ("rehabilitation_specific", "Rehabilitation Specific Tests"),
        ("cardiovascular", "Cardiovascular Tests"),
        ("sports_specific", "Sports-Specific Tests"),
        ("specialized_orthopedic", "Specialized Orthopedic Assessments"),
        ("neurological_specific", "Neurological Specific Tests"),
        ("ergonomic_workplace", "Ergonomic and Workplace Assessments"),
        ("pediatric", "Pediatric Physiotherapy Tests"),
        ("geriatric", "Geriatric Specific Tests"),
        ("other", "Other Tests"),
    ]
    category = models.CharField(null=True, choices=CATEGORY_CHOICES, max_length=300)
    name = models.CharField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.price}"
    

class PhysioRequest(models.Model):
    doctor = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='doctor')
    physiotherapist = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='physiotherapist')
    patient = models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE, related_name="physio_info")
    test = models.ForeignKey(PhysioTest, null=True, on_delete=models.CASCADE)
    payment = models.OneToOneField(Paypoint, null=True, on_delete=models.CASCADE, related_name="physio_payment")
    diagnosis = models.CharField(max_length=200, null=True, blank=True)
    remark = models.CharField(max_length=200, null=True, blank=True)
    comment=QuillField(null=True, blank=True)
    request_date = models.DateTimeField(null=True,auto_now_add=True)
    result_details=QuillField(null=True, blank=True)
    result_date = models.DateTimeField(null=True, blank=True)
    cleared = models.BooleanField(default=False)
    
    updated = models.DateTimeField(null=True,auto_now=True)

    def save(self, *args, **kwargs):
        if self.result_details and not self.result_date:
            self.result_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient} - {self.test.name}"
    
class RadiologyResult(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    test = models.ForeignKey(RadiologyTest, max_length=100, null=True, blank=True, on_delete=models.CASCADE, related_name="radiology_results")
    patient = models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE, related_name="radiology_results")
    cleared = models.BooleanField(default=False)
    comments=QuillField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'radiology results'

    def __str__(self):
        return str(self.patient)


class RadiologyTests(models.Model):
    radiology_test = models.ForeignKey(RadiologyResult, null=True, on_delete=models.CASCADE, related_name="radiology_result")
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='radiology_test_items',null=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,null=True)
    payment = models.ForeignKey(Paypoint, null=True, on_delete=models.CASCADE, related_name="radiology_payment")
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"RADIOLOGY REQUEST"

class RadiologyInvestigations(models.Model):
    radiologytest = models.ForeignKey(RadiologyTests, on_delete=models.CASCADE, related_name='radiology_items', null=True)
    item = models.ForeignKey(RadiologyTest, on_delete=models.CASCADE, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.radiologytest.patient.file_no} {self.item.name}"
    
    @property
    def total_item_price(self):
        return self.item.price if self.item else 0
    