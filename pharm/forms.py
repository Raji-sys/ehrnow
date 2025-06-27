from django import forms
from .models import *
from django.forms import DateInput
class DrugForm(forms.ModelForm):
    expiration_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    
    class Meta:
        model = Drug
        fields = ['name','trade_name','strength','supplier','dosage_form','pack_size','cost_price','selling_price','total_purchased_quantity','supply_date','expiration_date']  
        widgets = {
            'supply_date': DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(DrugForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required=False    
            field.widget.attrs.update({'class':'text-center text-xs md:text-xs focus:outline-none border border-blue-300 p-2 sm:p-3 rounded shadow-lg hover:shadow-xl p-2'})



# class RecordForm(forms.ModelForm):
#     class Meta:
#         model = Record
#         fields = ['category', 'drug', 'unit_issued_to', 'quantity']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
#         for field in self.fields.values():
#             field.required = False
#             field.widget.attrs.update({'class': 'text-center text-xs focus:outline-none border border-blue-300 p-3 rounded shadow-lg hover:shadow-xl'})

#     def clean(self):
#         cleaned_data = super().clean()
#         quantity = cleaned_data.get('quantity')
#         drug = cleaned_data.get('drug')
#         unit_issued_to = cleaned_data.get('unit_issued_to')

#         if drug and quantity is not None and unit_issued_to:
#             with transaction.atomic():
#                 drug.refresh_from_db()
#                 available_quantity = drug.current_balance

#                 if self.instance.pk:
#                     # This is an update
#                     original_record = Record.objects.get(pk=self.instance.pk)
#                     net_quantity_change = quantity - original_record.quantity
                    
#                     if net_quantity_change > available_quantity:
#                         self.add_error('quantity', f"Warning: Only {available_quantity} additional units available. Please adjust the issued quantity.")
#                 else:
#                     # This is a new record
#                     if quantity > available_quantity:
#                         self.add_error('quantity', f"Warning: Only {available_quantity} units available. Please adjust the issued quantity.")

#         return cleaned_data
class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = [ 'drug', 'unit_issued_to', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Removed: self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
        for field_name, field in self.fields.items():
            field.required = False # Keep this as per your original logic
            if field_name == 'drug':
                # We will hide the original drug select widget using JavaScript/CSS
                # and use a text input for autocomplete.
                # The original select will store the actual drug ID.
                field.widget.attrs.update({
                    'class': 'original-drug-select text-center text-xs focus:outline-none border border-blue-300 p-3 rounded shadow-lg hover:shadow-xl'
                })
            else:
                 field.widget.attrs.update({
                    'class': 'text-center text-xs focus:outline-none border border-blue-300 p-3 rounded shadow-lg hover:shadow-xl'
                })


    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        drug = cleaned_data.get('drug') # This will be the Drug instance
        unit_issued_to = cleaned_data.get('unit_issued_to')

        # Ensure all necessary fields are present before proceeding with stock validation
        # This check is important because fields are not required.
        if not (drug and quantity is not None and unit_issued_to):
            # If any of the core fields for a line item are missing,
            # we assume this line item is intentionally left blank and skip stock validation for it.
            # The formset's overall validation (e.g., at least one form filled)
            # is handled in the view.
            return cleaned_data

        # Proceed with stock validation only if drug, quantity, and unit_issued_to are provided
        # Using select_for_update to lock the drug row during the transaction
        try:
            # Refresh drug instance within a transaction to get the latest data and lock the row
            # This requires the clean method to be part of a transaction if called during save.
            # However, clean methods are typically called before the save transaction begins.
            # For robust stock checking, it's often better to do this final check
            # within the view's transaction block, right before saving.
            # For now, we'll keep your existing logic.
            # drug_for_check = Drug.objects.select_for_update().get(pk=drug.pk)
            # available_quantity = drug_for_check.current_balance
            
            # Simpler refresh for now, be mindful of potential race conditions without select_for_update
            # if not handled at a higher level (e.g. in the view's transaction.atomic block)
            drug.refresh_from_db()
            available_quantity = drug.current_balance

            if self.instance and self.instance.pk: # Checking if instance exists and has a PK
                # This is an update
                original_record = Record.objects.get(pk=self.instance.pk)
                if original_record.drug == drug: # If drug hasn't changed
                    net_quantity_change = quantity - original_record.quantity
                    if net_quantity_change > 0 and net_quantity_change > available_quantity : # only check if increasing quantity
                         self.add_error('quantity', f"Warning: Only {available_quantity} additional units of '{drug.name}' available. You tried to issue {net_quantity_change} more.")
                elif quantity > available_quantity: # If drug has changed, check full quantity
                     self.add_error('quantity', f"Warning: Only {available_quantity} units of '{drug.name}' available. Please adjust.")
            else:
                # This is a new record
                if quantity > available_quantity:
                    self.add_error('quantity', f"Warning: Only {available_quantity} units of '{drug.name}' available. Please adjust the issued quantity.")
        except Drug.DoesNotExist:
            self.add_error('drug', "Selected drug not found. Please try again.")
        
        return cleaned_data

class RestockForm(forms.ModelForm):
    class Meta:
        model = Restock
        fields = ['category', 'drug', 'quantity','expiration_date']
        widgets = {
            'expiration_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
        for field in self.fields.values():
            field.required = True
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-blue-300 p-3 rounded shadow-lg hover:shadow-xl'
            })


class UnitIssueRecordForm(forms.ModelForm):
    class Meta:
        model = UnitIssueRecord
        fields = ['unit', 'category', 'drug', 'quantity', 'issued_to']
        # fields = ['unit', 'category', 'drug', 'quantity', 'issued_to']
        # widgets = {
        #     'date_issued': forms.DateInput(attrs={'type': 'date'}),
        # }

    def __init__(self, *args, **kwargs):
        self.issuing_unit = kwargs.pop('issuing_unit', None)
        super(UnitIssueRecordForm, self).__init__(*args, **kwargs)
        self.fields['unit'].widget.attrs['readonly'] = True
        self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
        if self.issuing_unit:
            self.fields['issued_to'].queryset = Unit.objects.exclude(id=self.issuing_unit.id)
        for field in self.fields.values():
            field.required = False
            field.widget.attrs.update({'class':'text-center text-xs md:text-xs focus:outline-none border border-blue-300 p-2 sm:p-3 rounded shadow-lg hover:shadow-xl p-2'})

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None:
            raise forms.ValidationError("Quantity is required.")
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        unit = cleaned_data.get('unit')
        issued_to = cleaned_data.get('issued_to')
        issued_to_locker = cleaned_data.get('issued_to_locker')
        drug = cleaned_data.get('drug')
        quantity = cleaned_data.get('quantity')

        if issued_to and issued_to_locker:
            self.add_error(None, "Cannot issue to both a unit and a locker at the same time.")
        if not issued_to and not issued_to_locker:
            self.add_error(None, "Must issue to either a unit or a locker.")
        if unit and issued_to and unit == issued_to:
            self.add_error(None, "A unit cannot issue drugs to itself.")

        # Skip validation if any required field is missing
        if not all([unit, drug, quantity]):
            return cleaned_data

        # Validate that the unit has enough of the drug available
        unit_store = UnitStore.objects.filter(unit=unit, drug=drug).first()
        if not unit_store:
            self.add_error('drug', f"{drug.name} is not available in {unit.name}'s store.")
        elif unit_store.quantity < quantity:
            self.add_error('quantity', f"Not enough {drug.name} in {unit.name}'s store. Available: {unit_store.quantity}")

        return cleaned_data


class BoxRecordForm(forms.ModelForm):
    class Meta:
        model = UnitIssueRecord
        fields = ['unit', 'category', 'drug', 'quantity', 'moved_to']
        # widgets = {
        #     'date_issued': forms.DateInput(attrs={'type': 'date'}),
        # }

    def __init__(self, *args, **kwargs):
        self.issuing_unit = kwargs.pop('issuing_unit', None)
        super(BoxRecordForm, self).__init__(*args, **kwargs)
        self.fields['unit'].widget.attrs['readonly'] = True
        self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
        if self.issuing_unit:
            self.fields['moved_to'].queryset = Box.objects.exclude(id=self.issuing_unit.id)
        for field in self.fields.values():
            field.required = False
            field.widget.attrs.update({'class':'text-center text-xs md:text-xs focus:outline-none border border-blue-300 p-2 sm:p-3 rounded shadow-lg hover:shadow-xl p-2'})

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None:
            raise forms.ValidationError("Quantity is required.")
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        unit = cleaned_data.get('unit')
        moved_to = cleaned_data.get('issued_to')
        drug = cleaned_data.get('drug')
        quantity = cleaned_data.get('quantity')

        # Skip validation if any required field is missing
        if not all([unit, drug, quantity]):
            return cleaned_data

        # Validate that the unit has enough of the drug available
        unit_store = UnitStore.objects.filter(unit=unit, drug=drug).first()
        if not unit_store:
            self.add_error('drug', f"{drug.name} is not available in {unit.name}'s store.")
        elif unit_store.quantity < quantity:
            self.add_error('quantity', f"Not enough {drug.name} in {unit.name}'s store. Available: {unit_store.quantity}")

        return cleaned_data


# class DispensaryIssueRecordForm(forms.ModelForm):
#     class Meta:
#         model = UnitIssueRecord

#         fields = ['unit', 'drug', 'quantity', 'issued_to_locker']

#     def __init__(self, *args, **kwargs):
#         self.issuing_unit = kwargs.pop('issuing_unit', None)
#         super(DispensaryIssueRecordForm, self).__init__(*args, **kwargs)
#         self.fields['unit'].widget.attrs['readonly'] = True
#         self.fields['issued_to_locker'].widget.attrs['readonly'] = True
#         if self.issuing_unit:
#             self.fields['issued_to_locker'].queryset = DispensaryLocker.objects.filter(unit=self.issuing_unit)
#         for field in self.fields.values():
#             field.required = False
#             field.widget.attrs.update({'class':'text-center text-xs md:text-xs focus:outline-none border border-blue-300 p-2 sm:p-3 rounded shadow-lg hover:shadow-xl p-2'})

#     def clean_quantity(self):
#         quantity = self.cleaned_data.get('quantity')
#         if quantity is None:
#             raise forms.ValidationError("Quantity is required.")
#         if quantity <= 0:
#             raise forms.ValidationError("Quantity must be greater than zero.")
#         return quantity

#     def clean(self):
#         cleaned_data = super().clean()
#         unit = cleaned_data.get('unit')
#         issued_to = cleaned_data.get('issued_to')
#         issued_to_locker = cleaned_data.get('issued_to_locker')
#         drug = cleaned_data.get('drug')
#         quantity = cleaned_data.get('quantity')

#         if issued_to and issued_to_locker:
#             self.add_error(None, "Cannot issue to both a unit and a locker at the same time.")
#         if not issued_to and not issued_to_locker:
#             self.add_error(None, "Must issue to either a unit or a locker.")
#         if unit and issued_to and unit == issued_to:
#             self.add_error(None, "A unit cannot issue drugs to itself.")

#         # Skip validation if any required field is missing
#         if not all([unit, drug, quantity]):
#             return cleaned_data

#         # Validate that the unit has enough of the drug available
#         unit_store = UnitStore.objects.filter(unit=unit, drug=drug).first()
#         if not unit_store:
#             self.add_error('drug', f"{drug.name} is not available in {unit.name}'s store.")
#         elif unit_store.quantity < quantity:
#             self.add_error('quantity', f"Not enough {drug.name} in {unit.name}'s store. Available: {unit_store.quantity}")

#         return cleaned_data
# Updated DispensaryIssueRecordForm
class DispensaryIssueRecordForm(forms.ModelForm):
    class Meta:
        model = UnitIssueRecord
        fields = ['unit', 'drug', 'quantity', 'issued_to_locker']

    def __init__(self, *args, **kwargs):
        self.issuing_unit = kwargs.pop('issuing_unit', None)
        super(DispensaryIssueRecordForm, self).__init__(*args, **kwargs)
        
        # Set unit and issued_to_locker fields as readonly
        self.fields['unit'].widget.attrs['readonly'] = True
        self.fields['issued_to_locker'].widget.attrs['readonly'] = True

        # Filter queryset for issued_to_locker if issuing_unit is provided
        if self.issuing_unit:
            self.fields['issued_to_locker'].queryset = DispensaryLocker.objects.filter(unit=self.issuing_unit)

        # Apply common styling to all fields
        for field_name, field in self.fields.items():
            field.required = False # Keep fields not required as per original logic
            if field_name == 'drug':
                # This class will be used to hide the original select element via JavaScript
                # and ensure it has basic styling if it somehow becomes visible.
                field.widget.attrs.update({
                    'class': 'original-drug-select text-center text-xs focus:outline-none border border-blue-300 p-2 sm:p-3 rounded shadow-lg hover:shadow-xl'
                })
            else:
                field.widget.attrs.update({
                    'class': 'text-center text-xs md:text-xs focus:outline-none border border-blue-300 p-2 sm:p-3 rounded shadow-lg hover:shadow-xl p-2'
                })

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None:
            # If quantity is not provided, don't raise an error here.
            # The overall clean method will handle cases where core fields are missing.
            return quantity
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        unit = cleaned_data.get('unit')
        issued_to = cleaned_data.get('issued_to') # Note: This field is not in Meta.fields, might be a typo from original context.
                                                  # Assuming 'issued_to_locker' is the relevant target.
        issued_to_locker = cleaned_data.get('issued_to_locker')
        drug = cleaned_data.get('drug')
        quantity = cleaned_data.get('quantity')

        # Basic validation for destination (unit or locker)
        # Note: 'issued_to' is not in the form's fields. Assuming 'issued_to_locker' is the target.
        # If 'issued_to' is meant to be a field for issuing to a unit, it needs to be added to Meta.fields.
        # For now, I'll adapt based on the provided fields.
        if issued_to_locker and not issued_to_locker: # This condition is redundant if issued_to is not a field.
            self.add_error(None, "Must issue to a locker.") # Adjusted message if only locker is an option.

        # Skip validation if any core field for a line item is missing.
        # This allows for empty forms in a formset.
        if not (drug and quantity is not None and unit): # 'quantity is not None' to allow 0 if needed, but clean_quantity handles > 0
            return cleaned_data

        # Validate that the unit has enough of the drug available
        try:
            # Refresh unit_store instance within a transaction to get the latest data and lock the row
            # For robust stock checking, it's often better to do this final check
            # within the view's transaction block, right before saving.
            # For now, we'll keep your existing logic.
            unit_store = UnitStore.objects.get(unit=unit, drug=drug)
            available_quantity = unit_store.quantity

            if self.instance and self.instance.pk: # This is an update
                original_record = UnitIssueRecord.objects.get(pk=self.instance.pk)
                if original_record.drug == drug: # If drug hasn't changed
                    net_quantity_change = quantity - original_record.quantity
                    if net_quantity_change > 0 and net_quantity_change > available_quantity:
                        self.add_error('quantity', f"Warning: Only {available_quantity} additional units of '{drug.name}' available in {unit.name}'s store. You tried to issue {net_quantity_change} more.")
                elif quantity > available_quantity: # If drug has changed, check full quantity
                    self.add_error('quantity', f"Warning: Only {available_quantity} units of '{drug.name}' available in {unit.name}'s store. Please adjust.")
            else: # This is a new record
                if quantity > available_quantity:
                    self.add_error('quantity', f"Not enough {drug.name} in {unit.name}'s store. Available: {available_quantity}. You tried to issue {quantity}.")
        except UnitStore.DoesNotExist:
            self.add_error('drug', f"{drug.name} is not available in {unit.name}'s store.")
        except Exception as e:
            self.add_error(None, f"An error occurred during stock validation: {e}")

        return cleaned_data

# class DispenseRecordForm(forms.ModelForm):
#     class Meta:
#         model = DispenseRecord
#         fields = ['drug', 'quantity',]

#     def __init__(self, *args, **kwargs):
#         self.dispensary = kwargs.pop('dispensary', None)
#         self.patient = kwargs.pop('patient', None)
#         super(DispenseRecordForm, self).__init__(*args, **kwargs)
#         self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
        
#         if self.dispensary:
#             self.fields['drug'].queryset = Drug.objects.filter(
#                 lockerinventory__locker=self.dispensary,
#                 lockerinventory__quantity__gt=0
#             ).distinct()

#         for field in self.fields.values():
#             field.required = False
#             field.widget.attrs.update({'class': 'text-center text-xs md:text-xs focus:outline-none border border-blue-300 p-2 sm:p-3 rounded shadow-lg hover:shadow-xl p-2'})

#     def clean(self):
#         cleaned_data = super().clean()
#         drug = cleaned_data.get('drug')
#         quantity = cleaned_data.get('quantity')

#         if not drug or not quantity:
#             return cleaned_data

#         if quantity <= 0:
#             raise forms.ValidationError("Quantity must be greater than zero.")

#         try:
#             inventory = LockerInventory.objects.get(locker=self.dispensary, drug=drug)
#             if quantity > inventory.quantity:
#                 raise forms.ValidationError(f"Not enough {drug} in inventory. Available: {inventory.quantity}")
#         except LockerInventory.DoesNotExist:
#             raise forms.ValidationError(f"{drug} is not available in this dispensary.")

#         return cleaned_data
    
class DispenseRecordForm(forms.ModelForm):
    class Meta:
        model = DispenseRecord
        fields = ['drug', 'quantity']

    def __init__(self, *args, **kwargs):
        self.dispensary = kwargs.pop('dispensary', None)
        self.patient = kwargs.pop('patient', None)
        super(DispenseRecordForm, self).__init__(*args, **kwargs)
        
        # Remove the category field handling since we're not using it anymore
        # self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
        
        if self.dispensary:
            # Keep your existing inventory filtering
            self.fields['drug'].queryset = Drug.objects.filter(
                lockerinventory__locker=self.dispensary,
                lockerinventory__quantity__gt=0
            ).distinct()
        else:
            # Initialize with empty queryset for autocomplete
            self.fields['drug'].queryset = Drug.objects.none()

        for field in self.fields.values():
            field.required = False
            field.widget.attrs.update({
                'class': 'text-center text-xs md:text-xs focus:outline-none border border-blue-300 p-2 sm:p-3 rounded shadow-lg hover:shadow-xl p-2'
            })

    def clean(self):
        cleaned_data = super().clean()
        drug = cleaned_data.get('drug')
        quantity = cleaned_data.get('quantity')

        if not drug or not quantity:
            return cleaned_data

        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")

        try:
            inventory = LockerInventory.objects.get(locker=self.dispensary, drug=drug)
            if quantity > inventory.quantity:
                raise forms.ValidationError(f"Not enough {drug} in inventory. Available: {inventory.quantity}")
        except LockerInventory.DoesNotExist:
            raise forms.ValidationError(f"{drug} is not available in this dispensary.")

        return cleaned_data
    
class ReturnDrugForm(forms.ModelForm):
    class Meta:
        model = ReturnedDrugs
        fields = ['category', 'drug', 'quantity', 'patient_info',]

    def __init__(self, *args, **kwargs):
        self.unit = kwargs.pop('unit', None)
        super(ReturnDrugForm, self).__init__(*args, **kwargs) 
        self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
        
        if self.unit:
            # Adjust this queryset as needed based on your specific requirements for returns
            self.fields['drug'].queryset = Drug.objects.filter(
                unit_store_drugs__unit=self.unit
            ).distinct()

        for field in self.fields.values():
            field.required = False
            field.widget.attrs.update({
                'class': 'text-center text-xs md:text-xs focus:outline-none border border-blue-300 p-2 sm:p-3 rounded shadow-lg hover:shadow-xl p-2'
            })

    def clean(self):
        cleaned_data = super().clean()
        drug = cleaned_data.get('drug')
        quantity = cleaned_data.get('quantity')

        if not drug or not quantity:
            return cleaned_data

        if quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")


        return cleaned_data

class DispenseForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        initial=True,  # Changed to True since we want it checked by default
        widget=forms.HiddenInput()  # Simplified widget definition
    )


# class PrescriptionForm(forms.ModelForm):
#     class Meta:
#         model = Prescription
#         fields = ['category', 'drug', 'dose']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['category'].widget.attrs.update({'onchange': 'load_drugs()'})
#         for field in self.fields.values():
#             field.required = False
#             field.widget.attrs.update({
#                 'class': 'text-center text-xs focus:outline-none border border-green-400 p-2 rounded shadow-lg focus:shadow-xl focus:border-green-200'
#             })

#     def clean(self):
#         cleaned_data = super().clean()
#         quantity = cleaned_data.get('quantity')
#         drug = cleaned_data.get('drug')
        
#         if drug and quantity:
#             if not drug.has_sufficient_stock(quantity):
#                 raise ValidationError(
#                     f"Insufficient stock. Available: {drug.current_balance}, Requested: {quantity}"
#                 )
        
#         return cleaned_data


# class PrescriptionUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Prescription
#         fields = ['category','drug','quantity','dose']
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields.values():
#             field.required=False    
#             field.widget.attrs.update({'class': 'text-center text-xs focus:outline-none border border-green-400  p-2 rounded shadow-lg focus:shadow-xl focus:border-green-200'})

class PrescriptionForm(forms.ModelForm):
    categories = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'id': 'category-selector'})
    )

    class Meta:
        model = Prescription
        fields = ['dose']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required=False
            field.widget.attrs.update({'class': 'text-center text-xs focus:outline-none border border-green-400  p-2 rounded shadow-lg focus:shadow-xl focus:border-green-200'})
