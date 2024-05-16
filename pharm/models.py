from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from ehr.models import PatientData,Paypoint
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Unit(models.TextChoices):
    ACCIDENT_AND_EMERGENCY = 'A & E', 'A & E'
    IN_PATIENT = 'IN-PATIENT', 'IN-PATIENT'
    NHIS = 'NHIS', 'NHIS'
    SPINE = 'SPINE', 'SPINE'
    SOPD = 'SOPD', 'SOPD'
    THEATRE = 'THEATRE', 'THEATRE'

class Category(models.Model):
    name = models.CharField('CLASS OF DRUG',max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

class Drug(models.Model):
    date_added = models.DateField('DATE DRUG WAS ADDED',auto_now_add=True)
    name = models.CharField('DRUG NAME',max_length=100, unique=True)
    generic_name = models.CharField('GENERIC NAME',max_length=100, null=True, blank=True)
    brand_name = models.CharField('BRAND NAME',max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    supplier = models.CharField('SUPPLIER',max_length=100, null=True, blank=True)
    dosage_form = models.CharField('DOSAGE FORM',max_length=100, null=True, blank=True)
    pack_price = models.DecimalField('PACK PRICE',max_digits=100, decimal_places=2, null=True, blank=True)
    pack_size = models.CharField('PACK SIZE',max_length=100, null=True, blank=True)
    cost_price = models.DecimalField('COST PRICE',max_digits=10, decimal_places=2, null=True, blank=True)
    total_purchased_quantity = models.PositiveIntegerField('TOTAL QTY PURCHASED',default=0)
    expiration_date = models.DateField('DATE ADDED',null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_drugs')
    updated_at = models.DateField('DATE UPDATED',auto_now=True)

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
    unit_issued_to = models.CharField('PHARMACY UNIT ISSUED TO',max_length=100, choices=Unit.choices, null=True, blank=True)
    siv = models.CharField('SIV',max_length=100, null=True, blank=True)
    srv = models.CharField('SRV',max_length=100, null=True, blank=True)
    invoice_no = models.PositiveIntegerField('INVOICE NUMBER',null=True, blank=True)
    quantity = models.PositiveIntegerField('QTY ISSUED',null=True, blank=True)
    balance = models.PositiveIntegerField('CURRENT BALANCE',null=True, blank=True)
    date_issued = models.DateField('DATE DRUG WAS ISSUED',auto_now_add=True)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='drug_records')
    remark = models.CharField('REMARKS',max_length=100, choices=Unit.choices, null=True, blank=True)
    updated_at = models.DateTimeField('DATE UPDATED',auto_now=True)

    def save(self, *args, **kwargs):
        if self.balance is None:
            self.balance = self.drug.current_balance

        quantity_to_issue = min(self.quantity, self.balance)

        if quantity_to_issue <= 0:
            raise ValidationError(_("Not allowed."), code='invalid_quantity')

        self.quantity = quantity_to_issue
        self.balance -= quantity_to_issue
        super().save(*args, **kwargs)
        self.drug.save()

    def __str__(self):
        return self.drug.name

    class Meta:
        verbose_name_plural = 'drugs issued record'

class Dispensary(models.Model):
    patient = models.ForeignKey(PatientData,null=True, blank=True, on_delete=models.CASCADE,related_name='dispensed_drugs')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name="dispensary_drug_catgory")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True, blank=True, related_name="dispensary_drug")
    payment = models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('QTY TO DISPENSE',null=True, blank=True)
    balance = models.PositiveIntegerField('CURRENT BALANCE',null=True, blank=True)
    dispensed_date = models.DateField('DISPENSE DATE',auto_now_add=True)
    dispensed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='dispensed_by')
    remark = models.CharField('REMARKS',max_length=100, choices=Unit.choices, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.balance is None:
            self.balance = self.drug.current_balance
        quantity_to_dispense = min(self.quantity, self.balance)

        if quantity_to_dispense <= 0:
            raise ValidationError(_("Not allowed."), code='not enough quantity')

        self.quantity = quantity_to_dispense
        self.balance -= quantity_to_dispense
        super().save(*args, **kwargs)

        self.drug.save()

    def __str__(self):
        return f"{self.patient}--{self.drug.name}--{self.dispensed_date}"

    class Meta:
        verbose_name_plural = 'dispensary record'


class Purchase(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, null=True,)
    quantity_purchased = models.IntegerField()
    # expiration_date = models.DateField(null=True, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the total_purchased_quantity field in the associated drug model
        self.drug.total_purchased_quantity += self.quantity_purchased
        self.drug.save()

    def __str__(self):
        return f"{self.quantity_purchased} of {self.drug.name} purchased on {self.purchase_date}"

    class Meta:
        verbose_name_plural = 'purchases record'