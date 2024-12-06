from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta
import logging
logger = logging.getLogger(__name__)
from ehr.models import PatientData, Paypoint

class Unit(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    update = models.DateField(auto_now_add=True, null=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating:
            DispensaryLocker.objects.create(unit=self)

    def total_unit_value(self):
        store_value = sum(
            store.total_value for store in self.unit_store.all()
            if store.total_value is not None
        )
        locker_value = 0
        if hasattr(self, 'dispensary_locker'):
            locker_value = self.dispensary_locker.inventory.aggregate(
                total=Sum(F('drug__cost_price') * F('quantity'))
            )['total'] or 0
        return store_value + locker_value

    def total_unit_quantity(self):
        store_quantity = sum(
            store.quantity for store in self.unit_store.all()
        )
        locker_quantity = 0
        if hasattr(self, 'dispensary_locker'):
            locker_quantity = self.dispensary_locker.inventory.aggregate(
                total=Sum('quantity')
            )['total'] or 0
        return store_quantity + locker_quantity

    @classmethod
    def combined_unit_value(cls):
        return sum(unit.total_unit_value() for unit in cls.objects.all())

    @classmethod
    def combined_unit_quantity(cls):
        return sum(unit.total_unit_quantity() for unit in cls.objects.all())

    @classmethod
    def grand_total_value(cls):
        main_store_value = Drug.total_store_value()
        combined_unit_value = cls.combined_unit_value()
        return main_store_value + combined_unit_value

    @classmethod
    def grand_total_quantity(cls):
        main_store_quantity = Drug.total_store_quantity()  # Assuming you've added this method to the Drug model
        combined_unit_quantity = cls.combined_unit_quantity()
        return main_store_quantity + combined_unit_quantity

    def __str__(self):
        return self.name


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
    date_added = models.DateField(auto_now_add=True,null=True)
    supply_date = models.DateField(null=True)
    strength = models.CharField('STRENGTH',max_length=100, null=True, blank=True)
    name = models.CharField('GENERIC NAME',max_length=100, null=True, blank=True)
    trade_name = models.CharField('TRADE NAME',max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='drug_category')
    supplier = models.CharField('SUPPLIER',max_length=100, null=True, blank=True)
    dosage=(('TABLET','TABLET'),('CAPSULE','CAPSULE'),('SYRUP','SYRUP'),('INJECTION','INJECTION'),('INFUSION','INFUSION'),('SUSPENSION','SUSPENSION'),('SOLUTION','SOLUTION'),('CONSUMABLE','CONSUMABLE'),('POWDER','POWDER'),('GRANULE','GRANULE'),('PELLET','PELLET'),
            ('EMULSION','EMULSION'),('TINCTURE','TINCTURE'),('OINTMENT','OINMENT'),('CREAM','CREAM'),('GEL','GEL'),('SUPPOSITORY','SUPPOSITORY'),('INHALER','INHALER'),('IMPLANT','IMPLANT'),('LOZENGE','LOZENGEN'),('SPRAY','SPRAY'),('TRANSDERMAL PATCH','TRANSDERMAL PATCH'))
    dosage_form = models.CharField(choices=dosage,max_length=100, null=True, blank=True)
    pack_size = models.CharField('PACK SIZE',max_length=100, null=True, blank=True)
    cost_price = models.DecimalField('COST PRICE',max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_purchased_quantity = models.PositiveIntegerField('TOTAL QTY PURCHASED',default=0)
    expiration_date = models.DateField(null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_drugs')
    entered_expiry_period = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField('DATE UPDATED',auto_now=True)

    def save(self, *args, **kwargs):
        if self.expiration_date:
            six_months_before = self.expiration_date - timedelta(days=180)
            if timezone.now().date() >= six_months_before and not self.entered_expiry_period:
                self.entered_expiry_period = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    @classmethod
    def total_store_quantity(cls):
        return sum(drug.total_purchased_quantity - drug.total_issued for drug in cls.objects.all())    
    
    @property
    def total_value(self):
        return self.current_balance * self.cost_price if self.current_balance is not None and self.cost_price is not None else 0

    @classmethod
    def total_store_value(cls):
        total_store_value = sum(drug.total_value for drug in cls.objects.all() if drug.total_value is not None)
        return total_store_value

    @property
    def total_issued(self):
        return self.drug_records.aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    @property
    def current_balance(self):
        return self.total_purchased_quantity - self.total_issued

    class Meta:
        verbose_name_plural = 'drugs'
    

class Record(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name="drug_records")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True, blank=True, related_name="drug_records")
    unit_issued_to = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    siv = models.CharField('SIV', max_length=100, null=True, blank=True)
    srv = models.CharField('SRV', max_length=100, null=True, blank=True)
    invoice_no = models.PositiveIntegerField('INVOICE NUMBER', null=True, blank=True)
    quantity = models.PositiveIntegerField('QTY ISSUED', null=True, blank=True)
    date_issued = models.DateField(null=True)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='drug_records')
    remark = models.CharField('REMARKS', max_length=200, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                original_record = Record.objects.select_for_update().get(pk=self.pk)
                net_quantity_change = self.quantity - original_record.quantity

                # Handle unit store updates
                if original_record.unit_issued_to != self.unit_issued_to:
                    # Remove quantity from old unit
                    UnitStore.objects.filter(
                        unit=original_record.unit_issued_to,
                        drug=original_record.drug
                    ).update(quantity=F('quantity') - original_record.quantity)

                    # Add quantity to new unit
                    new_unit_store, created = UnitStore.objects.get_or_create(
                        unit=self.unit_issued_to,
                        drug=self.drug,
                        defaults={'quantity': 0}
                    )
                    new_unit_store.quantity = F('quantity') + self.quantity
                    new_unit_store.save()
                else:
                    # Update quantity in the same unit
                    UnitStore.objects.filter(
                        unit=self.unit_issued_to,
                        drug=self.drug
                    ).update(quantity=F('quantity') + net_quantity_change)

            else:  # New record
                # Add quantity to the unit store
                unit_store, created = UnitStore.objects.get_or_create(
                    unit=self.unit_issued_to,
                    drug=self.drug,
                    defaults={'quantity': 0}
                )
                unit_store.quantity = F('quantity') + self.quantity
                unit_store.save()

            super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'drugs issued record'


class Restock(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='restock_category')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True,)
    quantity = models.IntegerField()
    date = models.DateField(null=True)
    expiration_date = models.DateField(null=True, blank=True)
    restocked_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='drug_restocking')
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.drug.total_purchased_quantity += self.quantity
        self.drug.save()

    def __str__(self):
        return f"{self.quantity} of {self.drug} restocked on {self.date}"

    class Meta:
        verbose_name_plural = 'restocking record'

class UnitStore(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='unit_store')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='unit_store_drugs')
    quantity = models.PositiveIntegerField('Quantity Available', default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_value(self):
        return self.quantity * self.drug.cost_price

    def __str__(self):
        return f"{self.quantity} of {self.drug.name} in {self.unit.name}"

class DispensaryLocker(models.Model):
    unit = models.OneToOneField(Unit, on_delete=models.CASCADE, related_name='dispensary_locker')
    name = models.CharField(max_length=100, default="Dispensary Locker")
    
    def __str__(self):
        return f"{self.unit.name} {self.name}"

class LockerInventory(models.Model):
    locker = models.ForeignKey(DispensaryLocker, on_delete=models.CASCADE, related_name='inventory')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['locker', 'drug']

    def __str__(self):
        return f"{self.drug} in {self.locker}"

class Box(models.Model):
    name=models.CharField(max_length=200, null=True, blank=True)
    update=models.DateField(auto_now_add=True,null=True)
    
    def __str__(self):
        return self.name

class UnitIssueRecord(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='issuing_unit')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='unitissue_category')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='issued_drugs')
    quantity = models.PositiveIntegerField(null=True, blank=True)
    date_issued = models.DateTimeField(auto_now_add=True,null=True)
    issued_to = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='receiving_unit', null=True, blank=True)
    moved_to = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='box_moved', null=True, blank=True)
    issued_to_locker = models.ForeignKey(DispensaryLocker, on_delete=models.CASCADE, null=True, blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    updated_at = models.DateField(auto_now=True)
    
    
    def save(self, *args, **kwargs):
        unit_store = UnitStore.objects.get(unit=self.unit, drug=self.drug)
        
        if self.quantity > unit_store.quantity:
            raise ValidationError(_("Not enough drugs in the unit store."), code='invalid_quantity')
        
        # Deduct from the issuing unit's store
        unit_store.quantity -= self.quantity
        unit_store.save()

        # Add to the receiving unit's store if applicable
        if self.issued_to:
            receiving_store, created = UnitStore.objects.get_or_create(unit=self.issued_to, drug=self.drug)
            receiving_store.quantity += self.quantity
            receiving_store.save()
        super().save(*args, **kwargs)


class Prescription(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='dispense_unit',null=True,blank=True)
    patient = models.ForeignKey(PatientData, null=True, blank=True, on_delete=models.CASCADE, related_name='prescribed_drugs')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name="prescribed_drug_catgory")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True, blank=True, related_name="prescribed_drug")
    payment = models.ForeignKey(Paypoint, null=True, on_delete=models.CASCADE, related_name="pharm_payment")
    quantity = models.PositiveIntegerField('QTY', null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True)
    prescribed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='prescribed_by')
    prescribed_date = models.DateTimeField(auto_now=True,null=True,blank=True)
    dose = models.CharField('dosage', max_length=300, null=True, blank=True)
    remark = models.CharField('REMARKS', max_length=100, null=True, blank=True)
    is_dispensed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    @property
    def price(self):
        if self.drug.cost_price and self.quantity:
            return self.drug.cost_price * self.quantity

    def __str__(self):
        return f"{self.patient}"
    
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


class DispenseRecord(models.Model):
    dispensary = models.ForeignKey(DispensaryLocker, on_delete=models.CASCADE, related_name='issuing_dispensary')
    patient = models.ForeignKey(PatientData, null=True, blank=True, on_delete=models.CASCADE, related_name='dispensed_drugs')
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE, related_name='dispensary_rel',null=True,blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='dispensary_category')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='dispense_drugs')
    quantity = models.PositiveIntegerField('QTY ISSUED', null=True, blank=True)
    dispensed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    dispense_date = models.DateTimeField(auto_now=True)
    updated = models.DateField(auto_now=True)
    
    def clean(self):
        pass    
    
    def save(self, *args, **kwargs):
        dispense_locker = LockerInventory.objects.get(locker=self.dispensary, drug=self.drug)
        if self.quantity > dispense_locker.quantity:
            raise ValidationError(_("Not enough drugs in the unit store."), code='invalid_quantity')
        # Deduct from the dispensary locker
        dispense_locker.quantity -= self.quantity
        dispense_locker.save()
        super().save(*args, **kwargs)


class ReturnedDrugs(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='returned_drugs',null=True)  # New field
    patient_info = models.CharField(max_length=100,null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True, related_name='returned_category')
    drug = models.ForeignKey('Drug', on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(null=True)
    date = models.DateField(null=True)
    received_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='drug_returning')
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.drug.total_purchased_quantity += self.quantity
        self.drug.save()

    def __str__(self):
        return f"{self.quantity} of {self.drug} returned to {self.unit} on {self.date}"

    class Meta:
        verbose_name_plural = 'returned drugs record'

from django.db import models
from django.core.validators import MinValueValidator

class PrescriptionDrug(models.Model):
    prescription = models.ForeignKey(
        'Prescription', 
        on_delete=models.CASCADE, 
        related_name='prescription_drugs'
    )
    drug = models.ForeignKey(
        'Drug', 
        on_delete=models.CASCADE, 
        related_name='prescription_instances'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of the specific drug"
    )
    dosage = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Specific dosage instructions"
    )

    class Meta:
        unique_together = ('prescription', 'drug')
        verbose_name_plural = "Prescription Drugs"

    def __str__(self):
        return f"{self.drug.name} - {self.quantity}"