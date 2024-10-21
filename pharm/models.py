from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from ehr.models import PatientData,Paypoint
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

class Unit(models.TextChoices):
    ACCIDENT_AND_EMERGENCY = 'A & E', 'A & E'
    IN_PATIENT = 'IN-PATIENT', 'IN-PATIENT'
    NHIS = 'NHIS', 'NHIS'
    SPINE = 'SPINE', 'SPINE'
    SOPD = 'SOPD', 'SOPD'
    THEATRE = 'THEATRE', 'THEATRE'

from django.db import models

class Category(models.Model):
    DRUG_CLASSES = [
        ('ANALGESICS', 'Analgesics'),
        ('ANESTHETICS', 'Anesthetics'),
        ('ANTIBIOTICS', 'Antibiotics'),
        ('ANTICOAGULANTS', 'Anticoagulants'),
        ('ANTICONVULSANTS', 'Anticonvulsants'),
        ('ANTIDEPRESSANTS', 'Antidepressants'),
        ('ANTIDIABETICS', 'Antidiabetics'),
        ('ANTIEMETICS', 'Antiemetics'),
        ('ANTIFUNGALS', 'Antifungals'),
        ('ANTIHISTAMINES', 'Antihistamines'),
        ('ANTIHYPERTENSIVES', 'Antihypertensives'),
        ('ANTI_INFLAMMATORIES', 'Anti-inflammatories'),
        ('ANTINEOPLASTICS', 'Antineoplastics'),
        ('ANTIPARASITICS', 'Antiparasitics'),
        ('ANTIPSYCHOTICS', 'Antipsychotics'),
        ('ANTIVIRALS', 'Antivirals'),
        ('BRONCHODILATORS', 'Bronchodilators'),
        ('CARDIOVASCULAR', 'Cardiovascular'),
        ('CNS_STIMULANTS', 'CNS Stimulants'),
        ('CORTICOSTEROIDS', 'Corticosteroids'),
        ('DERMATOLOGICALS', 'Dermatologicals'),
        ('DIURETICS', 'Diuretics'),
        ('GASTROINTESTINAL', 'Gastrointestinal'),
        ('HORMONES', 'Hormones'),
        ('IMMUNOSUPPRESSANTS', 'Immunosuppressants'),
        ('LIPID_LOWERING', 'Lipid-lowering'),
        ('MUSCLE_RELAXANTS', 'Muscle Relaxants'),
        ('NSAIDS', 'NSAIDs'),
        ('OPIOIDS', 'Opioids'),
        ('OPHTHALMICS', 'Ophthalmics'),
        ('PSYCHOTROPICS', 'Psychotropics'),
        ('SEDATIVES_HYPNOTICS', 'Sedatives/Hypnotics'),
        ('THYROID_PREPARATIONS', 'Thyroid Preparations'),
        ('VACCINES', 'Vaccines'),
        ('VITAMINS_MINERALS', 'Vitamins and Minerals'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField('CLASS OF DRUG', max_length=200, choices=DRUG_CLASSES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

class Drug(models.Model):
    date_added = models.DateField('DATE DRUG WAS ADDED', auto_now_add=True)
    name = models.CharField('DRUG NAME', max_length=100, unique=True)
    status = models.BooleanField(default=True)
    generic_name = models.CharField('GENERIC NAME', max_length=100, null=True, blank=True)
    brand_name = models.CharField('BRAND NAME', max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    supplier = models.CharField('SUPPLIER', max_length=100, null=True, blank=True)
    dosage_form = models.CharField('DOSAGE FORM', max_length=100, null=True, blank=True)
    pack_price = models.DecimalField('PACK PRICE', max_digits=100, decimal_places=2, null=True, blank=True)
    pack_size = models.CharField('PACK SIZE', max_length=100, null=True, blank=True)
    cost_price = models.DecimalField('COST PRICE', max_digits=10, decimal_places=2, null=True, blank=True)
    total_purchased_quantity = models.PositiveIntegerField('TOTAL QTY PURCHASED', default=0)
    total_issued = models.PositiveIntegerField('TOTAL QTY ISSUED', default=0)
    expiration_date = models.DateField('DATE ADDED', null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_drugs')
    updated_at = models.DateTimeField('DATE UPDATED', auto_now=True)

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        return self.current_balance * self.pack_price if self.current_balance is not None and self.pack_price is not None else 0

    @classmethod
    def total_store_value(cls):
        total_store_value = sum(drug.total_value for drug in cls.objects.all() if drug.total_value is not None)
        return total_store_value

    @property
    def current_balance(self):
        # return self.total_purchased_quantity - self.total_issued
        return max(0, self.total_purchased_quantity - self.total_issued)
    
    def has_sufficient_stock(self, requested_quantity):
        """Check if there's enough stock for the requested quantity"""
        return self.current_balance >= requested_quantity
    
    # def is_available(self):
    #     if self.current_balance is not None and self.current_balance <= 0:
    #         self.status = False
    #         self.save()  # Save the instance after updating the status
    #     return self.status

    class Meta:
        verbose_name_plural = 'drugs'


class Record(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name="drug_records")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True, blank=True, related_name="drug_records")
    unit_issued_to = models.CharField('PHARMACY UNIT ISSUED TO',max_length=100, choices=Unit.choices, null=True, blank=True)
    siv = models.CharField('SIV',max_length=100, null=True, blank=True)
    srv = models.CharField('SRV',max_length=100, null=True, blank=True)
    invoice_no = models.PositiveIntegerField('INVOICE NUMBER',null=True, blank=True)
    quantity = models.PositiveIntegerField('QTY ISSUED',null=True, blank=True)
    date_issued = models.DateTimeField('DATE DRUG WAS ISSUED',auto_now_add=True)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='drug_records')
    remark = models.CharField('REMARKS',max_length=100, choices=Unit.choices, null=True, blank=True)
    updated_at = models.DateTimeField('DATE UPDATED',auto_now=True)
    def save(self, *args, **kwargs):
        if self.pk:
            # Update existing instance
            self.drug.total_purchased_quantity -= self.quantity
            self.drug.save()
        else:
            # Create new instance
            self.drug.total_issued += self.quantity
            self.drug.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.drug.name

    class Meta:
        verbose_name_plural = 'drugs issued record'


class Prescription(models.Model):
    patient = models.ForeignKey(PatientData, null=True, blank=True, on_delete=models.CASCADE, related_name='prescribed_drugs')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name="prescribed_drug_catgory")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True, blank=True, related_name="prescribed_drug")
    payment = models.ForeignKey(Paypoint, null=True, on_delete=models.CASCADE, related_name="pharm_payment")
    quantity = models.PositiveIntegerField('QTY', null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True)
    prescribed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='prescribed_by')
    prescribed_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    dose = models.CharField('dosage', max_length=300, null=True, blank=True)
    remark = models.CharField('REMARKS', max_length=100, choices=Unit.choices, null=True, blank=True)
    is_dispensed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    @property
    def price(self):
        if self.drug.cost_price and self.quantity:
            return self.drug.cost_price * self.quantity

    def __str__(self):
        return self.patient.file_no
    
    def can_be_dispensed(self):
        """Check if the prescription can be dispensed"""
        if not self.drug or not self.quantity:
            return False, "Invalid prescription details"
        if not self.payment or not self.payment.status:
            return False, "Payment not completed"
        if self.is_dispensed:
            return False, "Already dispensed"
        if not self.drug.has_sufficient_stock(self.quantity):
            return False, f"Insufficient stock. Available: {self.drug.current_balance}, Requested: {self.quantity}"
        return True, "OK"
    
    class Meta:
        verbose_name_plural = 'prescription record'


class Dispensary(models.Model):
    patient = models.ForeignKey(PatientData, null=True, blank=True, on_delete=models.CASCADE, related_name='dispensed_drugs')
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE, related_name='dispensary',null=True,blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name="dispensary_drug_catgory")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True, blank=True, related_name="dispensary_drug")
    quantity = models.PositiveIntegerField('QTY TO DISPENSE', null=True, blank=True)
    dispensed_date = models.DateTimeField('DISPENSE DATE', auto_now_add=True)
    dispensed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='dispensed_by')
    remark = models.CharField('REMARKS', max_length=100, choices=Unit.choices, null=True, blank=True)
    quantity_deducted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.quantity_deducted and self.prescription:
            # Validate prescription can be dispensed
            can_dispense, message = self.prescription.can_be_dispensed()
            if not can_dispense:
                raise ValidationError(message)

            # Set related fields
            self.drug = self.prescription.drug
            self.quantity = self.prescription.quantity
            self.patient = self.prescription.patient
            self.category = self.drug.category

            # Update quantities using transaction
            with transaction.atomic():
                # Recheck stock within transaction to prevent race conditions
                if not self.drug.has_sufficient_stock(self.quantity):
                    raise ValidationError(f"Insufficient stock. Available: {self.drug.current_balance}, Requested: {self.quantity}")
                
                self.drug.total_purchased_quantity -= self.quantity
                # self.drug.total_issued += self.quantity
                self.drug.save()
                self.quantity_deducted = True
                
                # Mark prescription as dispensed
                self.prescription.is_dispensed = True
                self.prescription.save()

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.prescription.patient} - {self.prescription.drug}"
    class Meta:
        verbose_name_plural = 'dispensary record'


class Purchase(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True,)
    quantity_purchased = models.IntegerField()
    # expiration_date = models.DateField(null=True, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.drug.total_purchased_quantity += self.quantity_purchased
        self.drug.save()

    def __str__(self):
        return f"{self.quantity_purchased} of {self.drug.name} purchased on {self.purchase_date}"

    class Meta:
        verbose_name_plural = 'purchases record'