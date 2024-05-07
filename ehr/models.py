from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import timedelta, date
from django.db import models
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe

class SerialNumberField(models.CharField):
    description = "A unique serial number field with leading zeros"

    def __init__(self, *args, **kwargs):
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["unique"]
        return name, path, args, kwargs
    

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    dep = (
        ('INFORMATION TECH', 'INFORMATION TECH'),
        ('INTERNAL AUDIT', 'INTERNAL AUDIT'),
        ('REVENUE', 'REVENUE'),
        ('HMS', 'HMS'),
        ('DOCTORS', 'DOCTORS'),
        ('NURSES', 'NURSES'),
        ('PATHOLOGY', 'PATHOLOGY'),
        ('PHARMACY', 'PHARMACY'),
        ('PHYSIOTHERAPHY', 'PHYSIOTHERAPHY'),
        ('PROSTHETIC AND ORTHOTICS', 'PROSTHETIC AND ORTHOTICS'),
        ('RADIOLOGY', 'RADIOLOGY'),
    )
    department = models.CharField(choices=dep, blank=True, max_length=300, null=True)
    email = models.EmailField(blank=True, null=True,max_length=100, unique=True)
    phone = models.PositiveIntegerField(null=True, blank=True, unique=True)
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
        if self.user.username:
            return reverse('profile_details', args=[self.user.username])
        else:
            raise ImproperlyConfigured("User must have a non-empty username")
    
    def full_name(self):
        return f"{self.user.get_full_name()}"

    def __str__(self):
        if self.user:
            return f"{self.full_name()}"

class Clinic(models.Model):
    clinics=(('A & E','A & E'),('SOPD','SOPD'),('SPINE SOPD','SPINE SOPD'),('GOPD','GOPD'),('NHIS','NHIS'),('DENTAL','DENTAL'),
        ('O & G','O & G'),('UROLOGY','UROGOLY'),('DERMATOLOGY','DERMATOLOGY'),('PAEDIATRY','PAEDIATRY'))
    name = models.CharField(choices=clinics, null=True, blank=True, max_length=200, default='A & E')
    team=models.CharField(max_length=200,null=True,blank=True)
 
    def get_absolute_url(self):
        return reverse('clinic_details', args=[self.name])

    def __str__(self):
        if self.name:
            return f"{self.name}"

class Team(models.Model):
    teams=(('green','reen'),('purple','purple'),('white','white'),('blue','blue'),('pink','pink'),('plastic','plastic'),
        ('club foot','club foot'),)
    name = models.CharField(choices=teams, null=True, blank=True, max_length=200)
    team=models.CharField(max_length=200,null=True,blank=True)
 
    def get_absolute_url(self):
        return reverse('clinic_details', args=[self.name])

    def __str__(self):
        if self.name:
            return f"{self.name}"
        
class PatientData(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True, related_name='patients')
    file_no = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    other_name = models.CharField(max_length=300, blank=True, null=True)
    phone = models.PositiveIntegerField(null=True, blank=True, unique=True)
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
    occupation = models.CharField(max_length=300, null=True, blank=True)
    role_in_occupation = models.CharField(max_length=300, null=True, blank=True)
    nok_name = models.CharField('next of kin name', max_length=300, null=True, blank=True)
    nok_phone = models.PositiveIntegerField('next of kin phone', null=True, blank=True)
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
                new_file_no = f"{last_file_no + 1:07d}"  # 07 for 7 leading zeros
            else:
                new_file_no = "0000001"

            self.file_no = new_file_no

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('patient_details', args=[self.file_no])

    def full_name(self):
        return f"{self.title} {self.first_name} {self.last_name} {self.other_name}"

    def __str__(self):
        return self.full_name()
    
        
    def age(self):
        today = date.today()
        if self.dob:
            age = today.year - self.dob.year
            if today.month < self.dob.month or (today.month == self.dob.month and today.day < self.dob.day):
                age -= 1
            return age

    def is_birthday(self):
        today = date.today()
        if self.dob:
            return today.month == self.dob.month and today.day == self.dob.day
        return False


class ServiceType(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.CharField('TYPE OF SERVICE',max_length=200)
    def __str__(self):
        return self.name

class Services(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    type=models.ForeignKey(ServiceType,null=True, on_delete=models.CASCADE)
    name=models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'hospital services'

    def get_absolute_url(self):
        return reverse('service_details', args=[self.type])

class Paypoint(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    service=models.ForeignKey(Services,null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'),('paid', 'Paid'),], default='pending')
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])


class FollowUpVisit(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE)
    team = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True, related_name='teams')
    clinic=models.ForeignKey(Clinic, null=True, blank=True,on_delete=models.CASCADE, related_name='clinics')
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    created = models.DateTimeField('date', auto_now_add=True)


class PatientHandover(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='handovers')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True, related_name='handovers')
    team = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True, related_name='teams')
    status = models.CharField(max_length=30, choices=[
        ('waiting_for_payment', 'Waiting for Payment'),
        ('waiting_for_clinic_assignment', 'Waiting for Clinic Assignment'),
        ('waiting_for_vital_signs', 'Waiting for Vital Signs'),
        ('waiting_for_consultation', 'Waiting for Consultation'),
        ('seen_by_doctor', 'seen_by_doctor'),
        ('awaiting_review', 'awaiting_review'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class Appointment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='appointments')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    


class VitalSigns(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='vital_signs')
    body_temperature=models.CharField(max_length=10, null=True, blank=True)
    pulse_rate=models.CharField(max_length=10, null=True, blank=True)
    respiration_rate=models.CharField(max_length=10, null=True, blank=True)
    blood_pressure=models.CharField(max_length=10, null=True, blank=True)
    blood_oxygen=models.CharField(max_length=10, null=True, blank=True)
    blood_glucose=models.CharField(max_length=10, null=True, blank=True)
    weight=models.CharField(max_length=10, null=True, blank=True)
    height=models.CharField(max_length=10, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('vitals_details', args=[self.user])


class ClinicalNote(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='clinical_notes')
    note=models.TextField(null=True, blank=True)

    """
    this need the to be choice 
    """
    diagnosis = models.CharField(max_length=300, null=True, blank=True)
    prescription = models.CharField(max_length=300, null=True, blank=True)
    phatology = models.CharField(max_length=300, null=True, blank=True)
    radiology = models.CharField(max_length=300, null=True, blank=True)
    """
    a remainder for later
    """
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('clincal_note_details', args=[self.user])

    def __str__(self):
        return f"notes for: {self.patient.file_no}"

class Phatology(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Radiology(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Pharmacy(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"

    
class Physio(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Ward(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Theatre(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class ICU(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class NHIS(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    created = models.DateTimeField('transaction date', auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class PandO(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Audit(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"
