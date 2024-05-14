from django import forms
from .models import *

class DrugForm(forms.ModelForm):
    expiration_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    
    class Meta:
        model = Drug
        fields = ['name','generic_name','brand_name','category','supplier','dosage_form','pack_size','pack_price','cost_price','total_purchased_quantity','expiration_date']  

    def __init__(self, *args, **kwargs):
        super(DrugForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required=True    
            field.widget.attrs.update({'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['category', 'drug', 'unit_issued_to', 'quantity']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})  # Add onchange event
        for field in self.fields.values():
            field.required=True    
            field.widget.attrs.update({'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})

    def clean(self):
        cleaned_data=super().clean()
        quantity=cleaned_data.get('quantity')
        category=cleaned_data.get('category')
        drug=cleaned_data.get('drug')
        if drug is not None:
            balance=cleaned_data.get('drug').current_balance

        if quantity and balance is not None:
            quantity_to_issue=min(quantity,balance)
            if quantity_to_issue <= 0:
                raise forms.ValidationError("sorry, not enough drugs in your store")
        return cleaned_data


class DispenseForm(forms.ModelForm):
    class Meta:
        model = Dispensary
        fields = ['category','drug','quantity']

    def __init__(self, *args, **kwargs):
        super(DispenseForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
        for field in self.fields.values():
            # field.required=True
            field.widget.attrs.update(
                {'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'})

    def clean(self):
        cleaned_data=super().clean()
        quantity=cleaned_data.get('quantity')
        category=cleaned_data.get('category')
        drug=cleaned_data.get('drug')
        if drug is not None:
            balance=cleaned_data.get('drug').current_balance

        if quantity and balance is not None:
            quantity_to_issue=min(quantity,balance)
            if quantity_to_issue <= 0:
                raise forms.ValidationError("sorry, not enough drugs in your dispensary")
        return cleaned_data