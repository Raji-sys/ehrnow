from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import *
User = get_user_model()



class HematologyTestForm(forms.ModelForm):
    class Meta:
        model = HematologyResult
        fields = ['test']
    def __init__(self, *args, **kwargs):
        super(HematologyTestForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })



class HematologyResultForm(forms.ModelForm):
    class Meta:
        model = HematologyResult
        fields = ['test', 'result','cleared']
    def __init__(self, *args, **kwargs):
        super(HematologyResultForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class ChempathTestForm(forms.ModelForm):
    class Meta:
        model = ChemicalPathologyResult
        fields = ['test']
    def __init__(self, *args, **kwargs):
        super(ChempathTestForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class ChempathResultForm(forms.ModelForm):
    class Meta:
        model = ChemicalPathologyResult
        fields = ['test', 'result','cleared']
    def __init__(self, *args, **kwargs):
        super(ChempathResultForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class MicroTestForm(forms.ModelForm):
    class Meta:
        model = MicrobiologyResult
        fields = ['test']
    def __init__(self, *args, **kwargs):
        super(MicroTestForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class MicroResultForm(forms.ModelForm):
    class Meta:
        model = MicrobiologyResult
        fields = ['test', 'result','cleared']
    def __init__(self, *args, **kwargs):
        super(MicroResultForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class SerologyTestForm(forms.ModelForm):
    class Meta:
        model = SerologyResult
        fields = ['test']
    def __init__(self, *args, **kwargs):
        super(SerologyTestForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })

class SerologyResultForm(forms.ModelForm):
    class Meta:
        model = SerologyResult
        fields = ['test','result','cleared']
    def __init__(self, *args, **kwargs):
        super(SerologyResultForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class GeneralTestForm(forms.ModelForm):
    class Meta:
        model=GeneralTestResult
        fields=['name']
    def __init__(self, *args, **kwargs):
        super(GeneralTestForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })


class GeneralTestResultForm(forms.ModelForm):
    class Meta:
        model=GeneralTestResult
        fields=['result','comments','cleared']
    def __init__(self, *args, **kwargs):
        super(GeneralTestResultForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'text-center text-xs focus:outline-none border border-green-400 p-4 rounded shadow-lg focus:shadow-xl focus:border-green-200'
            })
