from django.db import models
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator


class CompanyAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField('account name',max_length=100, unique=True)
    account_number= models.CharField(max_length=20, unique=True)
    balance= models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created= models.DateField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Company Accounts'
    ordering = ['name']

    def clean(self):
        super().clean()
        if self.balance < 0:
            raise ValidationError(_("Balance cannot be negative"))

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

    def update_balance(self, amount):
        if amount < 0:
            raise ValidationError(_("Amount cannot be negative"))
        self.balance += amount
        self.save()

    def deduct_balance(self, amount):
        if amount < 0:
            raise ValidationError(_("Amount cannot be negative"))
        if self.balance - amount < 0:
            raise ValidationError(_("Insufficient balance"))
        self.balance -= amount
        self.save()


class CompanyExpense(models.Model):
    CATEGORY_CHOICES = [
        ('OFFICE', 'Office Supplies'),
        ('RENT', 'Rent & Utilities'),
        ('SALARY', 'Salaries'),
        ('SOFTWARE', 'Software Licenses'),
        ('MARKETING', 'Marketing'),
        ('TRAVEL', 'Business Travel'),
        ('EQUIPMENT', 'Equipment'),
        ('MAINTENANCE', 'Maintenance'),
        ('TAX', 'Taxes'),
        ('OTHER', 'Other Expenses'),
    ]
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('EcoBank I', 'EcoBank I'),
        ('EcoBank II', 'EcoBank II'),
        ('EcoBank III', 'EcoBank III'),
        ('Zenith Bank', 'Zenith Bank'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    vendor = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    account_used = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.CharField(max_length=1000, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    created = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.category}: ₦{self.amount} - {self.vendor}"
    
    def clean(self):
        super().clean()
        if self.amount <= 0:
            raise ValidationError(_("Amount must be positive"))
        if not self.category:
            raise ValidationError(_("Category is required"))
        if not self.account_used:
            raise ValidationError(_("Account used is required"))
            
        # For new expenses, check if there's enough balance
        if not self.pk and self.account_used and self.account_used.balance < self.amount:
            raise ValidationError(_("Insufficient balance in the selected account"))
        
        # For existing expenses, check if the balance difference is available
        if self.pk:
            try:
                original = CompanyExpense.objects.get(pk=self.pk)
                # If account changed, need to check both accounts
                if original.account_used != self.account_used:
                    # Check if new account has enough
                    if self.account_used.balance < self.amount:
                        raise ValidationError(_("Insufficient balance in the new selected account"))
                else:
                    # Same account, check if balance can handle the difference
                    if self.amount > original.amount:
                        difference = self.amount - original.amount
                        if self.account_used.balance < difference:
                            raise ValidationError(_("Insufficient balance for the increased expense amount"))
            except CompanyExpense.DoesNotExist:
                pass
    
    def save(self, *args, **kwargs):
        # Track if this is a new instance
        is_new = self.pk is None
        
        # If updating an existing expense
        if not is_new:
            # Get the original expense
            original = CompanyExpense.objects.get(pk=self.pk)
            
            # Handle the case where account has changed
            if original.account_used != self.account_used:
                # Refund the old account
                if original.account_used:
                    original.account_used.update_balance(original.amount)
                    
                # Deduct from the new account
                if self.account_used:
                    self.account_used.deduct_balance(self.amount)
            else:
                # Same account, handle the difference
                if original.amount != self.amount:
                    # Calculate the difference
                    difference = self.amount - original.amount
                    
                    if difference > 0:
                        # Amount increased, deduct the difference
                        self.account_used.deduct_balance(difference)
                    else:
                        # Amount decreased, add the difference back
                        self.account_used.update_balance(abs(difference))
        else:
            # This is a new expense, deduct the full amount
            if self.account_used:
                self.account_used.deduct_balance(self.amount)
            
        # Save the expense
        super().save(*args, **kwargs)
        
        # Record the transaction
        if hasattr(self, '_record_transaction'):
            Transaction.objects.create(
                account=self.account_used,
                amount=-self.amount if is_new else (original.amount - self.amount),
                description=f"Expense: {self.category} - {self.vendor}",
                transaction_type='WITHDRAWAL',
                created_by=self.user
            )
    
    def delete(self, *args, **kwargs):
        # Refund the account before deleting
        if self.account_used:
            self.account_used.update_balance(self.amount)
            
            # Record the transaction
            if hasattr(self, '_record_transaction'):
                Transaction.objects.create(
                    account=self.account_used,
                    amount=self.amount,
                    description=f"Expense Deleted: {self.category} - {self.vendor}",
                    transaction_type='DEPOSIT',
                    created_by=self.user
                )
                
        super().delete(*args, **kwargs)
        
      
    def get_update_url(self):
        return reverse('erp:expense_update', kwargs={'pk': self.pk})
        
    def get_delete_url(self):
        return reverse('erp:expense_delete', kwargs={'pk': self.pk})
        
    class Meta:
        ordering = ['-updated']
        verbose_name = 'Company Expense'
        verbose_name_plural = 'Company Expenses'




class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
    )
    
    account = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.transaction_type} of {self.amount} on {self.created}"
    
    class Meta:
        ordering = ['-created']