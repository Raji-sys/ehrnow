from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _
from django.apps import apps
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


class HematologyTest(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    reference_range = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class HematologyResult(models.Model):
    patient = models.ForeignKey('ehr.PatientData', on_delete=models.CASCADE, related_name='hematology_result', null=True, blank=True)
    result_code = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    test = models.ForeignKey(HematologyTest, max_length=100, null=True, blank=True, on_delete=models.CASCADE, related_name="results")
    result = QuillField(null=True, blank=True)
    comments=QuillField(null=True, blank=True)
    natured_of_specimen = models.CharField(max_length=1-0, null=True, blank=True)
    collected = models.DateField(auto_now=True, null=True,blank=True)
    reported = models.DateField(auto_now=True, null=True, blank=True)
    collected_by = models.ForeignKey(User, null=True, blank=True, related_name='hematology_results_collected', on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='hematology_results_reported', on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
 
    def get_patient_model(self):
        return apps.get_model('ehr', 'PatientData')
    
    def save(self, *args, **kwargs):
        if not self.result_code:
            last_instance = self.__class__.objects.order_by('result_code').last()

            if last_instance:
                last_result_code = int(last_instance.result_code.removeprefix('HEM'))
                new_result_code = f"HEM{last_result_code + 1:03d}"
            else:
                new_result_code = "HEM001"

            self.result_code = new_result_code

        super().save(*args, **kwargs)

    def __str__(self):
        if self.patient:
            return f"{self.patient.full_name()} - {self.test} - {self.result}"
        

class ChempathTestName(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}, {self.reference_range}"
    

class ChemicalPathologyResult(models.Model):
    patient = models.ForeignKey('ehr.PatientData', on_delete=models.CASCADE, related_name='chemical_pathology_results',null=True, blank=True)
    result_code = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    test = models.ForeignKey(ChempathTestName, max_length=100, null=True, blank=True, on_delete=models.CASCADE, related_name="results")
    result = models.FloatField(null=True, blank=True)
    comments=models.TextField(null=True, blank=True)
    natured_of_specimen = models.CharField(max_length=1-0, null=True, blank=True)
    collected = models.DateField(auto_now=True, null=True,blank=True)
    reported = models.DateField(auto_now=True, null=True, blank=True)
    collected_by = models.ForeignKey(User, null=True, blank=True, related_name='chempath_results_collected', on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='chempath_results_reported', on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_patient_model(self):
        return apps.get_model('ehr', 'PatientData')
    
    def save(self, *args, **kwargs):
        if not self.result_code:
            last_instance = self.__class__.objects.order_by('result_code').last()

            if last_instance:
                last_result_code = int(last_instance.result_code.removeprefix('CHP'))
                new_result_code = f"CHP{last_result_code + 1:03d}"
            else:
                new_result_code = "CHP001"

            self.result_code = new_result_code

        super().save(*args, **kwargs)

    def __str__(self):
        if self.patient:
            return f"{self.patient.surname} - {self.test} - {self.result}"
    

class MicrobiologyTest(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    reference_range = models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return self.name

class MicrobiologyResult(models.Model):
    patient = models.ForeignKey('ehr.PatientData', on_delete=models.CASCADE, related_name='microbiology_results',null=True, blank=True)
    result_code = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    test = models.ForeignKey(MicrobiologyTest, on_delete=models.CASCADE, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    comments=models.TextField(null=True, blank=True)
    natured_of_specimen = models.CharField(max_length=1-0, null=True, blank=True)
    collected = models.DateField(auto_now=True, null=True,blank=True)
    reported = models.DateField(auto_now=True, null=True, blank=True)
    collected_by = models.ForeignKey(User, null=True, blank=True, related_name='microbiology_results_collected', on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='microbiology_results_reported', on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def get_patient_model(self):
        return apps.get_model('ehr', 'PatientData')
    def save(self, *args, **kwargs):
        if not self.result_code:
            last_instance = self.__class__.objects.order_by('result_code').last()

            if last_instance:
                last_result_code = int(last_instance.result_code.removeprefix('MIC'))
                new_result_code = f"MIC{last_result_code + 1:03d}"
            else:
                new_result_code = "MIC001"

            self.result_code = new_result_code

        super().save(*args, **kwargs)

    def __str__(self):
        if self.patient:
            return f"{self.patient} -{self.test} - {self.result}"

    def __str__(self):
        return f"{self.name}: {self.value}"
    

class SerologyTestName(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name}, {self.reference_range}"

class SerologyResult(models.Model):
    patient = models.ForeignKey('ehr.PatientData', on_delete=models.CASCADE, related_name='serology_results', null=True, blank=True)
    result_code = SerialNumberField(max_length=20, unique=True, editable=False, default="")
    test = models.ForeignKey(SerologyTestName, on_delete=models.CASCADE, null=True, blank=True, related_name='results')
    result = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    nature_of_specimen = models.CharField(max_length=100, null=True, blank=True)
    collected = models.DateField(auto_now_add=True, null=True, blank=True)
    reported = models.DateField(auto_now=True, null=True, blank=True)
    collected_by = models.ForeignKey(User, null=True, blank=True, related_name='serology_results_collected', on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='serology_results_reported', on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
 
    def get_patient_model(self):
        return apps.get_model('ehr', 'PatientData')

    def save(self, *args, **kwargs):
        if not self.result_code:
            last_instance = SerologyResult.objects.order_by('result_code').last()
            if last_instance:
                last_result_code = int(last_instance.result_code.replace('SER', ''))
                new_result_code = f"SER{last_result_code + 1:03d}"
            else:
                new_result_code = "SER001"
            self.result_code = new_result_code
        super().save(*args, **kwargs)

    def __str__(self):
        parts = []
        if self.patient:
            parts.append(str(self.patient))
        if self.test:
            parts.append(str(self.test))
        if self.result:
            parts.append(str(self.result))
        return " - ".join(parts)

    def __str__(self):
        if self.patient:
            return f"{self.patient} - {self.test} - {self.result}"
        else:
            return f"{self.test} - {self.result}"


class GeneralTestResult(models.Model):
    name = models.CharField(max_length=100, null=True)
    patient = models.ForeignKey('ehr.PatientData', on_delete=models.CASCADE, related_name='general_results', null=True, blank=True)
    result_code = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    result = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    nature_of_specimen = models.CharField(max_length=100, null=True, blank=True)
    collected = models.DateField(auto_now_add=True, null=True, blank=True)
    reported = models.DateField(auto_now=True, null=True, blank=True)
    collected_by = models.ForeignKey(User, null=True, blank=True, related_name='general_results_collected', on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='general_results_reported', on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
 
    def get_patient_model(self):
        return apps.get_model('ehr', 'PatientData')
 
    def __str__(self):
        if self.patient:
            return f"{self.patient} -{self.test} - {self.result}"

    def save(self, *args, **kwargs):
        if not self.result_code:
            last_instance = self.__class__.objects.order_by('result_code').last()

            if last_instance:
                last_result_code = int(last_instance.result_code.removeprefix('GEN'))
                new_result_code = f"GEN{last_result_code + 1:03d}"
            else:
                new_result_code = "GEN001"

            self.result_code = new_result_code

        super().save(*args, **kwargs)

    def __str__(self):
        if self.patient:
            return f"{self.patient.surname} - {self.test} - {self.result}"