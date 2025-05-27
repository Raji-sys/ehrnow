from django import forms
from .models import *
from django.utils.translation import gettext as _


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = CompanyExpense
        fields = ['category','vendor', 'account_used', 'amount','notes']
        labels = {
            'account_used': 'Payment Method',
            'vendor': 'Payment To',
            'category': 'Type of Expense',
        }
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required=False
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-blue-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-blue-200'})


            
class CompanyAccountForm(forms.ModelForm):
    class Meta:
        model = CompanyAccount
        fields = ['name', 'account_number',]
    
    def __init__(self, *args, **kwargs):
        super(CompanyAccountForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-blue-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-blue-200'})
        
        # Make required fields actually required in the form
        self.fields['name'].required = True
        self.fields['account_number'].required = True
    
    def clean_balance(self):
        balance = self.cleaned_data.get('balance')
        if balance is not None and balance < 0:
            raise forms.ValidationError("Balance cannot be negative")
        return balance
            

class AccountTransactionForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'text-center text-xs focus:outline-none border border-blue-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-blue-200',
            'step': '0.01'
        })
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-center text-xs focus:outline-none border border-blue-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-blue-200'
        })
    )

class AccountTransferForm(forms.Form):
    source_account = forms.ModelChoiceField(
        queryset=CompanyAccount.objects.all(),
        widget=forms.Select(attrs={
            'class': 'text-center text-xs focus:outline-none border border-blue-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-blue-200'
        })
    )
    destination_account = forms.ModelChoiceField(
        queryset=CompanyAccount.objects.all(),
        widget=forms.Select(attrs={
            'class': 'text-center text-xs focus:outline-none border border-blue-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-blue-200'
        })
    )
    amount = forms.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'text-center text-xs focus:outline-none border border-blue-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-blue-200',
            'step': '0.01'
        })
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'text-center text-xs focus:outline-none border border-blue-400 p-3 rounded shadow-lg focus:shadow-xl focus:border-blue-200'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source_account')
        destination = cleaned_data.get('destination_account')
        amount = cleaned_data.get('amount')
        
        if source and destination and source == destination:
            raise forms.ValidationError(_("Source and destination accounts cannot be the same"))
        
        if source and amount and source.balance < amount:
            raise forms.ValidationError(_("Insufficient balance in source account"))
            
        return cleaned_data
