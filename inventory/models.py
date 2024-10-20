from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
    

class Department(models.Model):
    name=models.CharField(max_length=200)    

    def __str__(self):
        return self.name


class Unit(models.Model):
    name=models.CharField(max_length=200)    

    def __str__(self):
        return self.name


class Item(models.Model):
    date_added = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100, null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_items')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True, related_name='units')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    qty = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def total_value(self):
        return self.current_balance * self.unit_price if self.current_balance is not None and self.unit_price is not None else 0

    @classmethod
    def total_store_value(cls):
        total_store_value = sum(item.total_value for item in cls.objects.all() if item.total_value is not None)
        return total_store_value
    
    @property
    def total_issued(self):
        return self.records.aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    @property
    def current_balance(self):
        return self.qty - self.total_issued

    class Meta:
        verbose_name_plural = 'items'


class Record(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True, related_name="records")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True, related_name="records")
    issued_to = models.ForeignKey(Department, on_delete=models.CASCADE,  null=True, blank=True)
    quantity = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    date_issued = models.DateField(auto_now_add=True)
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='records')    
    balance = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.quantity is not None and self.quantity <= 0 and not settings.TESTING:
            raise ValidationError({'quantity':_("Quanity cannot be negative")})

    def save(self, *args, **kwargs):
        if self.balance is None:
            self.balance = self.item.current_balance
        quantity_to_issue = min(self.quantity, self.balance)

        if quantity_to_issue <= 0 and not settings.TESTING:
            raise ValidationError(_("not allowed."), code='invalid_quantity')

        self.quantity = quantity_to_issue
        self.balance -= quantity_to_issue

        self.clean()
        
        super().save(*args, **kwargs)
        self.item.save()

    def balance_percentage(self):
        if self.item.qty == 0:
            return 0
        return (self.balance / self.item.qty) * 100

    def __str__(self):
        return self.item.name

    class Meta:
        verbose_name_plural = 'items issued record'


class ReStock(models.Model):
    unit=models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True, related_name="restock_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_purchased = models.PositiveIntegerField()
    invoice_number=models.IntegerField(null=True, blank=True)
    store_receiving_voucher=models.CharField(max_length=30, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the qty field in the associated Item model
        self.item.qty += self.quantity_purchased
        self.item.save()

    def __str__(self):
        return f"{self.quantity_purchased} of {self.item.name} purchased on {self.purchase_date}"

    class Meta:
        verbose_name_plural = 'restocking record'