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

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    dep = (
        ('INFORMATION TECH', 'INFORMATION TECH'),
        ('INTERNAL AUDIT', 'INTERNAL AUDIT'),
        ('MEDICAL RECORD', 'MEDICAL RECORD'),
        ('DOCTORS', 'DOCTORS'),
        ('NURSES', 'NURSES'),
        ('PATHOLOGY', 'PATHOLOGY'),
        ('PHARMACY', 'PHARMACY'),
        ('PHYSIOTHERAPHY', 'PHYSIOTHERAPHY'),
        ('PROSTHETIC AND ORTHOTICS', 'PROSTHETIC AND ORTHOTICS'),
        ('OCCUPATIONAL THERAPHY', 'OCCUPATIONAL THERAPHY'),
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
        return reverse('profile_details', args=[self.user])

    def full_name(self):
        return f"{self.title} {self.user.get_full_name()} {self.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Clinic(models.Model):
    clinics=(
        ('A & E','A & E'),
        ('SOPD','SOPD'),
        ('SPINE SOPD','SPINE SOPD'),
        ('GOPD','GOPD'),
        ('NHIS','NHIS'),
        ('DENTAL','DENTAL'),
        ('O & G','O & G'),
        ('UROLOGY','UROGOLY'),
        ('DERMATOLOGY','DERMATOLOGY'),
        ('PAEDIATRY','PAEDIATRY'))
    name = models.CharField(choices=clinics, null=True, blank=True, max_length=200)

    def get_absolute_url(self):
        return reverse('clinic_details', args=[self.name])

    def __str__(self):
        if self.name:
            return f"{self.name}"
        

class PatientData(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    other_name = models.CharField(max_length=300, blank=True, null=True)
    # photo = models.ImageField(null=True, blank=True)
    file_no = models.DecimalField('file number', max_digits=6, decimal_places=0, null=True, unique=True, blank=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    sex = (('MALE', 'MALE'), ('FEMALE', 'FEMALE'))
    gender = models.CharField(choices=sex, max_length=10, null=True, blank=True)
    dob = models.DateField('date of birth', null=True, blank=True)
    phone = models.PositiveIntegerField(null=True, blank=True, unique=True)
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
    nok_rel = models.CharField('relationship with first next of kin', max_length=300, null=True, blank=True)
    # nok_photo = models.ImageField('first next of kin photo', null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('file_details', args=[self.file_no])

    def full_name(self):
        return f"{self.title} {self.user.get_full_name()} {self.other_name} - {self.file_no}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"

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


class Paypoint(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    status=models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class VitalSigns(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
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
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class ClinicalNote(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Phatology(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Radiology(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Pharmacy(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Physio(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Ward(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Theatre(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class ICU(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class NHIS(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
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
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"


class Audit(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.user])

    def full_name(self):
        return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

    def __str__(self):
        if self.user:
            return f"{self.full_name}"
