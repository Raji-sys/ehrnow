from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone
from django_quill.fields import QuillField

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
    middle_name = models.CharField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    department = models.ForeignKey(Department, blank=True, max_length=300, null=True, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, blank=True, max_length=300, null=True, on_delete=models.CASCADE)
    phone = models.PositiveIntegerField(null=True, blank=True, unique=True)
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


# class AEClinic(models.Model):
#     name = models.CharField(null=True, blank=True, max_length=200)
    
#     def get_absolute_url(self):
#         return reverse('ae_details', args=[self.pk])

#     def __str__(self):
#         if self.name:
#             return f"{self.name}"

# class SOPDClinic(models.Model):
#     name = models.CharField(null=True, blank=True, max_length=200)
    
#     def get_absolute_url(self):
#         return reverse('sopd_details', args=[self.pk])

#     def __str__(self):
#         if self.name:
#             return f"{self.name}"

class Team(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)
    
    def get_absolute_url(self):
        return reverse('team_details', args=[self.name])

    def __str__(self):
        if self.name:
            return f"{self.name}"
        
    
class PatientData(models.Model):
    file_no = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    title = models.CharField(max_length=7, null=True, blank=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    other_name = models.CharField(max_length=300, blank=True, null=True)
    phone = models.PositiveIntegerField(null=True, blank=True, unique=True)
    photo = models.ImageField(null=True, blank=True)
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
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
        ('SPINE SOPD', 'SPINE SOPD'),
        ('GOPD', 'GOPD')
    ]
    clinic = models.CharField(max_length=30, null=True, choices=CLINIC_CHOICES)
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

    # def is_birthday(self):
    #     today = date.today()
    #     if self.dob:
    #         return today.month == self.dob.month and today.day == self.dob.day
    #     return False

class Room(models.Model):
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
        ('SPINE SOPD', 'SPINE SOPD'),
        ('GOPD', 'GOPD')
    ]
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


class ServiceType(models.Model):
    name = models.CharField('TYPE OF SERVICE',max_length=200,null=True)
    def __str__(self):
        return self.name

class Services(models.Model):
    type=models.ForeignKey(ServiceType,null=True, on_delete=models.CASCADE)
    name=models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}---{self.price}"

    class Meta:
        verbose_name_plural = 'hospital services'

    def get_absolute_url(self):
        return reverse('service_details', args=[self.type])

class Paypoint(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
    service=models.ForeignKey(Services,null=True, on_delete=models.CASCADE)
    receipt_no=models.CharField('Receipt Number',null=True,blank=True,max_length=100)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'),('paid', 'Paid'),], default='pending')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateField(auto_now=True)

    def get_absolute_url(self):
        return reverse('pay_details', args=[self.service])

    def get_service_info(self):
        return f"{self.service.name} - {self.service.price}"
    

class FollowUpVisit(models.Model):
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
        ('SPINE SOPD', 'SPINE SOPD'),
        ('GOPD', 'GOPD')
    ]

    patient=models.ForeignKey(PatientData, null=True, on_delete=models.CASCADE,related_name='follow_up')
    clinic = models.CharField(max_length=30, null=True, choices=CLINIC_CHOICES)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    created = models.DateTimeField('date', auto_now_add=True)


class PatientHandover(models.Model):
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
        ('SPINE SOPD', 'SPINE SOPD'),
        ('GOPD', 'GOPD')
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
        ('seen', 'seen'),
        ('review', 'review'),
    ])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # class Meta:
    #     unique_together = ('patient', 'clinic', 'room')
    
class Appointment(models.Model):
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
        ('SPINE SOPD', 'SPINE SOPD'),
        ('GOPD', 'GOPD')
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
    


class VitalSigns(models.Model):
    ROOM_CHOICES = [
        ('ROOM 1', 'ROOM 1'),
        ('ROOM 2', 'ROOM 2'),
        ('ROOM 3', 'ROOM 3')
    ]
    CLINIC_CHOICES = [
        ('A & E', 'A & E'),
        ('SOPD', 'SOPD'),
        ('SPINE SOPD', 'SPINE SOPD'),
        ('GOPD', 'GOPD')
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

    def get_absolute_url(self):
        return reverse('vitals_details', args=[self.user])


class ClinicalNote(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE,related_name='clinical_notes')
    note=QuillField(null=True, blank=True)

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

# class Phatology(models.Model):
#     user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
#     patient=models.ForeignKey(PatientData,null=True, on_delete=models.CASCADE)
#     payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
#     updated = models.DateTimeField(auto_now=True)

#     def get_absolute_url(self):
#         return reverse('lab_details', args=[self.user])

#     def full_name(self):
#         return f"{self.user.profile.title} {self.user.get_full_name()} {self.profile.middle_name}"

#     def __str__(self):
#         if self.user:
#             return f"{self.full_name}"


# class Radiology(models.Model):
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


# class Pharmacy(models.Model):
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

    
# class Physio(models.Model):
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


# class Ward(models.Model):
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


# class Theatre(models.Model):
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


# class ICU(models.Model):
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
