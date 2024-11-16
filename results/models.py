from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django_quill.fields import QuillField
from django.contrib.auth import get_user_model
from ehr.models import PatientData, Paypoint
User = get_user_model()

    
class SerialNumberField(models.CharField):
    description = "A unique serial number field with leading zeros"

    def __init__(self, *args, **kwargs):
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["unique"]
        return name, path, args, kwargs

    
class GeneralTestResult(models.Model):
    test_1 = models.CharField(max_length=1000, null=True)
    result_1 = models.CharField(max_length=1000, null=True)
    reference_range_1 = models.CharField(max_length=1000, null=True)
    test_2 = models.CharField(max_length=1000, null=True)
    result_2 = models.CharField(max_length=1000, null=True)
    reference_range_2 = models.CharField(max_length=1000, null=True)
    test_3 = models.CharField(max_length=1000, null=True)
    result_3 = models.CharField(max_length=1000, null=True)
    reference_range_3 = models.CharField(max_length=1000, null=True)    
    test_4 = models.CharField(max_length=1000, null=True)
    result_4 = models.CharField(max_length=1000, null=True)
    reference_range_4 = models.CharField(max_length=1000, null=True)
    test_5 = models.CharField(max_length=1000, null=True)
    result_5 = models.CharField(max_length=1000, null=True)
    reference_range_5 = models.CharField(max_length=1000, null=True)
    test_6 = models.CharField(max_length=1000, null=True)
    result_6 = models.CharField(max_length=1000, null=True)
    reference_range_6 = models.CharField(max_length=1000, null=True)
    test_7 = models.CharField(max_length=1000, null=True)
    result_7 = models.CharField(max_length=1000, null=True)
    reference_range_7 = models.CharField(max_length=1000, null=True)
    test_8 = models.CharField(max_length=1000, null=True)
    result_8 = models.CharField(max_length=1000, null=True)
    reference_range_8 = models.CharField(max_length=1000, null=True)
    test_9 = models.CharField(max_length=1000, null=True)
    result_9 = models.CharField(max_length=1000, null=True)
    reference_range_9 = models.CharField(max_length=1000, null=True)
    test_10 = models.CharField(max_length=1000, null=True)
    result_10 = models.CharField(max_length=1000, null=True)
    reference_range_10 = models.CharField(max_length=1000, null=True)
    test_11 = models.CharField(max_length=1000, null=True)
    result_11 = models.CharField(max_length=1000, null=True)
    reference_range_11 = models.CharField(max_length=1000, null=True)
    test_12 = models.CharField(max_length=1000, null=True)
    result_12 = models.CharField(max_length=1000, null=True)
    reference_range_12 = models.CharField(max_length=1000, null=True)
    test_13 = models.CharField(max_length=1000, null=True)
    result_13 = models.CharField(max_length=1000, null=True)
    reference_range_13 = models.CharField(max_length=1000, null=True)
    test_14 = models.CharField(max_length=1000, null=True)
    result_14 = models.CharField(max_length=1000, null=True)
    reference_range_14 = models.CharField(max_length=1000, null=True)
    test_15 = models.CharField(max_length=1000, null=True)
    result_15 = models.CharField(max_length=1000, null=True)
    reference_range_15 = models.CharField(max_length=1000, null=True)
    payment=models.ForeignKey(Paypoint,null=True, on_delete=models.CASCADE,related_name='general_result_payment')
    price = models.DecimalField(max_digits=100, decimal_places=2, null=True,blank=True)
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='general_results', null=True, blank=True) 
    result_code = SerialNumberField(default="", editable=False,max_length=20,null=False,blank=True)
    cleared=models.BooleanField(default=False)
    # result = QuillField(null=True, blank=True)
    comments = models.CharField(max_length=500,null=True, blank=True)
    nature_of_specimen = models.CharField(max_length=300, null=True, blank=True)
    collected = models.DateField(auto_now_add=True, null=True, blank=True)
    collected_by = models.ForeignKey(User, null=True, blank=True, related_name='general_results_collected', on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='general_results_reported', on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
 
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
        parts = []
        if self.patient:
            parts.append(str(self.patient))
        if self.name:
            parts.append(str(self.name))
        if self.result:
            parts.append(str(self.result))
        return " - ".join(parts)

    def __str__(self):
        if self.patient:
            return f"{self.patient}"

class GenericTest(models.Model):
    LABS = [
        ('Chemical Pathology', 'Chemical Pathology'),
        ('Hematology', 'Hematology'),
        ('Microbiology', 'Microbiology'),
        ('Serology', 'Serology'),
        ('General', 'General')
    ]
    lab = models.CharField(choices=LABS, max_length=300,null=True, blank=True)
    name = models.CharField(max_length=1000, unique=True,null=True, blank=True)
    price = models.DecimalField(max_digits=100, decimal_places=2, null=True, blank=True)
    def __str__(self):        
        return f"{self.name} - {self.price}"

        
class Testinfo(models.Model):
    patient = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='test_info',null=True, blank=True)
    payment = models.ForeignKey(Paypoint, on_delete=models.CASCADE, related_name='test_payments',null=True,blank=True)
    code = models.CharField(max_length=20, unique=True, editable=False)
    cleared = models.BooleanField(default=False)
    comments = models.CharField(max_length=500, null=True, blank=True)
    nature_of_specimen = models.CharField(max_length=300, null=True, blank=True)
    collected = models.DateField(auto_now=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='collected_tests')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_tests')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} for {self.patient} - {self.updated}"
    def __str__(self):
        return f"{self.code} - {self.patient}"


# HEMATOLOGY TEST 
class FBC(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='fbc_test', null=True, blank=True)
    hb = models.CharField(max_length=10, null=True, blank=True)  # Hemoglobin
    pcv = models.CharField(max_length=10, null=True, blank=True)  # Packed Cell Volume
    mchc = models.CharField(max_length=10, null=True, blank=True)  # Mean Corpuscular Hemoglobin Concentration
    rbc = models.CharField(max_length=10, null=True, blank=True)  # Red Blood Cells
    mch = models.CharField(max_length=10, null=True, blank=True)  # Mean Corpuscular Hemoglobin
    mcv = models.CharField(max_length=10, null=True, blank=True)  # Mean Corpuscular Volume

    retic = models.CharField(max_length=10, null=True, blank=True)  # Reticulocyte Count
    retic_index = models.CharField(max_length=10, null=True, blank=True)  # Reticulocyte Index
    platelets = models.CharField(max_length=6,  null=True, blank=True)  # Platelets
    wbc = models.CharField(max_length=6, null=True, blank=True)  # White Blood Cells
    esr = models.CharField(max_length=6, null=True, blank=True)  # Erythrocyte Sedimentation Rate

    Opt= [
    ('+', '+'),
    ('++', '++'),
    ('+++', '+++'),
    ('None', 'None')
]

    sickle_cells = models.CharField(choices=Opt, max_length=100, null=True, blank=True)  # Sickle Cells
    hypochromia = models.CharField(choices=Opt, max_length=100, null=True, blank=True)  # Hypochromia
    polychromasia = models.CharField(choices=Opt, max_length=100, null=True, blank=True)  # Polychromasia
    nucleated_rbc = models.CharField(choices=Opt, max_length=100, null=True, blank=True)  # Nucleated RBC
    anisocytosis = models.CharField(choices=Opt, max_length=100, null=True, blank=True)  # Anisocytosis
    macrocytosis = models.CharField(choices=Opt, max_length=100, null=True, blank=True)  # Macrocytosis
    microcytosis = models.CharField(choices=Opt, max_length=100, null=True, blank=True)  # Microcytosis
    poikilocytosis = models.CharField(choices=Opt, max_length=100, null=True, blank=True)  # Poikilocytosis
    target_cells = models.CharField(choices=Opt, max_length=100, null=True, blank=True)  # Target Cells

    neutrophils = models.CharField(max_length=5,null=True, blank=True)  # Neutrophils %
    eosinophils = models.CharField(max_length=5,null=True, blank=True)  # Eosinophils %
    basophils = models.CharField(max_length=5, null=True, blank=True)  # Basophils %
    trans_lymph = models.CharField(max_length=10, null=True, blank=True)  # Transitional Lymphocytes %
    lymphocytes = models.CharField(max_length=10, null=True, blank=True)  # Lymphocytes %
    monocytes = models.CharField(max_length=10, null=True, blank=True)  # Monocytes %
    rbc_comments=models.CharField("RBC's",max_length=3000,null=True, blank=True)
    wbc_comments=models.CharField("WBC's",max_length=3000,null=True, blank=True)
    platelets_comments=models.CharField("Platelet's",max_length=3000,null=True, blank=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)


class BloodGroup(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='bg_test', null=True, blank=True)
    result = models.CharField(null=True, max_length=3, choices=BLOOD_GROUP_CHOICES)

    def get_absolute_url(self):
        return reverse('results:bg_test_details', args=[self.id])

    def __str__(self):
        return self.test


class Genotype(models.Model):
    GENOTYPE_CHOICES = [
        ('AA', 'AA'),
        ('AS', 'AS'),
        ('SS', 'SS'),
        ('AC', 'AC'),
        ('SC', 'SC'),
    ]

    test=models.ForeignKey(GenericTest,on_delete=models.CASCADE,null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='gt_test',null=True, blank=True)
    result = models.CharField(null=True,choices=GENOTYPE_CHOICES,max_length=2)


# CHEMICAL PATHOLOGY TESTS
class UreaAndElectrolyte(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='ue_test',null=True, blank=True)
    urea = models.CharField(max_length=100,null=True, blank=True)
    sodium = models.CharField(max_length=100,null=True, blank=True)
    potassium = models.CharField(max_length=100,null=True, blank=True)
    bicarbonate = models.CharField(max_length=100,null=True, blank=True)
    chloride = models.CharField(max_length=100,null=True, blank=True)
    creatinine = models.CharField(max_length=100,null=True, blank=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)


class LiverFunction(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='lf_test',null=True, blank=True)
    alkaline_phosphatase = models.CharField(max_length=100,null=True, blank=True)
    sgot = models.CharField(max_length=100,null=True, blank=True)
    sgpt = models.CharField(max_length=100,null=True, blank=True)
    gamma_gt = models.CharField(max_length=100,null=True, blank=True)
    total_bilirubin = models.CharField(max_length=100,null=True, blank=True)
    direct_bilirubin = models.CharField(max_length=100,null=True, blank=True)
    t_protein = models.CharField(max_length=10, help_text="Total Protein (g/dL)", null=True)
    albumin = models.CharField(max_length=10, help_text="Albumin (g/dL)", null=True)
    globulin = models.CharField(max_length=10, help_text="Globulin (g/dL)", null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)


class LipidProfile(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='lp_test',null=True, blank=True)
    cholesterol = models.CharField(max_length=100,null=True, blank=True)
    triglyceride = models.CharField(max_length=100,null=True, blank=True)
    hdl_cholesterol = models.CharField(max_length=100,null=True, blank=True)
    ldl_cholesterol = models.CharField(max_length=100,null=True, blank=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)


class BloodGlucose(models.Model):
    GLUCOSE_TEST_TYPES = [
        ('FASTING', 'Fasting'),
        ('RANDOM', 'Random'),
        ('2HR_PP', '2 Hour Post Prandial'),
    ]
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='bgl_test',null=True, blank=True)
    test_type = models.CharField(max_length=100, choices=GLUCOSE_TEST_TYPES,null=True)
    result = models.CharField(max_length=100,null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)


class SerumProteins(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='sp_test',null=True, blank=True)
    t_protein = models.CharField(max_length=10, help_text="Total Protein (g/dL)", null=True)
    albumin = models.CharField(max_length=10, help_text="Albumin (g/dL)", null=True)
    globulin = models.CharField(max_length=10, help_text="Globulin (g/dL)", null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)


class CerebroSpinalFluid(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='csf_test',null=True, blank=True)
    csf_glucose = models.CharField(max_length=10, help_text="CSF Glucose (mmol/L)", null=True)
    csf_protein = models.CharField(max_length=10, help_text="CSF Protein (mg/dL)", null=True)
    csf_chloride = models.CharField(max_length=10, help_text="CSF Chloride (mmol/L)", null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)


class BoneChemistry(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='bc_test',null=True, blank=True)
    alkaline_phosphatase = models.CharField(max_length=10, help_text="Alkaline Phosphatase (U/L)", null=True)
    calcium = models.CharField(max_length=10, help_text="Calcium (mmol/L)", null=True)
    inorganic_phosphate = models.CharField(max_length=10, help_text="Inorganic Phosphate (mmol/L)", null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)


class MiscellaneousChempathTests(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='misc_test',null=True, blank=True)
    uric_acid = models.CharField(max_length=10, help_text="Uric Acid (umol/L)", null=True,blank=True)
    serum_amylase = models.CharField(max_length=10, help_text="Serum Amylase (U/L)", null=True,blank=True)
    acid_phosphatase_total = models.CharField(max_length=10, help_text="Acid Phosphatase Total (U/L)", null=True,blank=True)
    acid_phosphatase_prostatic = models.CharField(max_length=10, help_text="Acid Phosphatase Prostatic (U/L)", null=True,blank=True)
    psa=models.CharField(max_length=10,null=True, blank=True, help_text="Prostate Specific Antigen (PSA)")
    comment = models.CharField(max_length=3000,null=True, blank=True)

# MICROBIOLOGY TEST 
SEVERITY_CHOICES = [
    ('s+', 's+'),
    ('s++', 's++'),
    ('s+++', 's+++'),
    ('R', 'R')
]
SWAB_PUS = [
    ('swab', 'swab'),
    ('pus', 'pus'),
    ('aspirate', 'aspirate'),
]
class Swab_Pus_Aspirate_MCS(models.Model):
    options=models.CharField(max_length=20,choices=SWAB_PUS,blank=True,null=True)
    test = models.ForeignKey('GenericTest', on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='swab_pus_aspirate_test', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True,null=True,blank=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

    # Culture yield fields with Yes/No options
    no_growth = models.BooleanField(default=False)
    e_coli = models.BooleanField(default=False)
    coliform = models.BooleanField(default=False)
    proteus = models.BooleanField(default=False)
    staph_aureus = models.BooleanField(default=False)
    pseudomonas = models.BooleanField(default=False)
    streptococcus = models.BooleanField(default=False)
    klebsiella = models.BooleanField(default=False)
    salmonella = models.BooleanField(default=False)
    str_feacalis = models.BooleanField(default=False)
    shigella = models.BooleanField(default=False)
    c_diphtheriae = models.BooleanField(default=False)
    neisseria = models.BooleanField(default=False)
    candida = models.BooleanField(default=False)
    haemophilus = models.BooleanField(default=False)
    str_pneumonia = models.BooleanField(default=False)
    str_pyogenes = models.BooleanField(default=False)
    staph_albus = models.BooleanField(default=False)
    usual_flora = models.BooleanField(default=False)
 
    # Antibiotics Sensitivity with Severity (1-4 and Resistant)
    cloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ciprofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    lincomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    flucloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    tetracycline = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ampicillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    erythromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    roxithromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    augmentin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cotrimoxazole = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cephalexin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    dalacin_c = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    gentamycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    streptomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftriaxone = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    chloramphenicol = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nitrofurantoin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nalidixic_acid = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cefuroxime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftazidime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    pefloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)


class UrineMicroscopy(models.Model):

    test = models.ForeignKey('GenericTest', on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='urine_test', null=True, blank=True)
    pus_cells = models.CharField(max_length=50, blank=True, null=True)
    rbc = models.CharField(max_length=50, blank=True, null=True)
    epithelial_cells = models.CharField(max_length=50, blank=True, null=True)
    casts = models.CharField(max_length=50, blank=True, null=True)
    crystals = models.CharField(max_length=50, blank=True, null=True)
    ova = models.CharField(max_length=50, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

    # Culture yield fields with Yes/No options
    no_growth = models.BooleanField(default=False)
    e_coli = models.BooleanField(default=False)
    coliform = models.BooleanField(default=False)
    proteus = models.BooleanField(default=False)
    staph_aureus = models.BooleanField(default=False)
    pseudomonas = models.BooleanField(default=False)
    streptococcus = models.BooleanField(default=False)
    klebsiella = models.BooleanField(default=False)
    salmonella = models.BooleanField(default=False)
    str_feacalis = models.BooleanField(default=False)
    shigella = models.BooleanField(default=False)
    c_diphtheriae = models.BooleanField(default=False)
    neisseria = models.BooleanField(default=False)
    candida = models.BooleanField(default=False)
    haemophilus = models.BooleanField(default=False)
    str_pneumonia = models.BooleanField(default=False)
    str_pyogenes = models.BooleanField(default=False)
    staph_albus = models.BooleanField(default=False)
    usual_flora = models.BooleanField(default=False)
 
    # Antibiotics Sensitivity with Severity (1-4 and Resistant)
    cloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ciprofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    lincomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    flucloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    tetracycline = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ampicillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    erythromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    roxithromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    augmentin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cotrimoxazole = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cephalexin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    dalacin_c = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    gentamycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    streptomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftriaxone = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    chloramphenicol = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nitrofurantoin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nalidixic_acid = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cefuroxime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftazidime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    pefloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)


class HVS(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='hvs_test',null=True, blank=True)
    pus_cells = models.CharField(max_length=50, blank=True, null=True)
    rbc = models.CharField(max_length=50, blank=True, null=True)
    epithelial_cells = models.CharField(max_length=50, blank=True, null=True)
    t_vaginalis = models.CharField(max_length=50, blank=True, null=True)
    yeast_cells = models.CharField(max_length=50, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

    # Culture yield fields with Yes/No options
    no_growth = models.BooleanField(default=False)
    e_coli = models.BooleanField(default=False)
    coliform = models.BooleanField(default=False)
    proteus = models.BooleanField(default=False)
    staph_aureus = models.BooleanField(default=False)
    pseudomonas = models.BooleanField(default=False)
    streptococcus = models.BooleanField(default=False)
    klebsiella = models.BooleanField(default=False)
    salmonella = models.BooleanField(default=False)
    str_feacalis = models.BooleanField(default=False)
    shigella = models.BooleanField(default=False)
    c_diphtheriae = models.BooleanField(default=False)
    neisseria = models.BooleanField(default=False)
    candida = models.BooleanField(default=False)
    haemophilus = models.BooleanField(default=False)
    str_pneumonia = models.BooleanField(default=False)
    str_pyogenes = models.BooleanField(default=False)
    staph_albus = models.BooleanField(default=False)
    usual_flora = models.BooleanField(default=False)
 
    # Antibiotics Sensitivity with Severity (1-4 and Resistant)
    cloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ciprofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    lincomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    flucloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    tetracycline = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ampicillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    erythromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    roxithromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    augmentin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cotrimoxazole = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cephalexin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    dalacin_c = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    gentamycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    streptomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftriaxone = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    chloramphenicol = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nitrofurantoin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nalidixic_acid = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cefuroxime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftazidime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    pefloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)



class Stool(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='stool_test',null=True, blank=True)
    consistency = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    mucus = models.CharField(max_length=50, blank=True, null=True)
    blood = models.CharField(max_length=50, blank=True, null=True)
    ova = models.CharField(max_length=50, blank=True, null=True)
    cyst = models.CharField(max_length=50, blank=True, null=True)
    others = models.CharField(max_length=50, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

    # Culture yield fields with Yes/No options
    no_growth = models.BooleanField(default=False)
    e_coli = models.BooleanField(default=False)
    coliform = models.BooleanField(default=False)
    proteus = models.BooleanField(default=False)
    staph_aureus = models.BooleanField(default=False)
    pseudomonas = models.BooleanField(default=False)
    streptococcus = models.BooleanField(default=False)
    klebsiella = models.BooleanField(default=False)
    salmonella = models.BooleanField(default=False)
    str_feacalis = models.BooleanField(default=False)
    shigella = models.BooleanField(default=False)
    c_diphtheriae = models.BooleanField(default=False)
    neisseria = models.BooleanField(default=False)
    candida = models.BooleanField(default=False)
    haemophilus = models.BooleanField(default=False)
    str_pneumonia = models.BooleanField(default=False)
    str_pyogenes = models.BooleanField(default=False)
    staph_albus = models.BooleanField(default=False)
    usual_flora = models.BooleanField(default=False)
 
    # Antibiotics Sensitivity with Severity (1-4 and Resistant)
    cloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ciprofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    lincomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    flucloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    tetracycline = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ampicillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    erythromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    roxithromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    augmentin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cotrimoxazole = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cephalexin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    dalacin_c = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    gentamycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    streptomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftriaxone = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    chloramphenicol = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nitrofurantoin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nalidixic_acid = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cefuroxime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftazidime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    pefloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)



class BloodCulture(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='blood_culture_test',null=True, blank=True)
    result=models.CharField(max_length=300,null=True,blank=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

    # Culture yield fields with Yes/No options
    no_growth = models.BooleanField(default=False)
    e_coli = models.BooleanField(default=False)
    coliform = models.BooleanField(default=False)
    proteus = models.BooleanField(default=False)
    staph_aureus = models.BooleanField(default=False)
    pseudomonas = models.BooleanField(default=False)
    streptococcus = models.BooleanField(default=False)
    klebsiella = models.BooleanField(default=False)
    salmonella = models.BooleanField(default=False)
    str_feacalis = models.BooleanField(default=False)
    shigella = models.BooleanField(default=False)
    c_diphtheriae = models.BooleanField(default=False)
    neisseria = models.BooleanField(default=False)
    candida = models.BooleanField(default=False)
    haemophilus = models.BooleanField(default=False)
    str_pneumonia = models.BooleanField(default=False)
    str_pyogenes = models.BooleanField(default=False)
    staph_albus = models.BooleanField(default=False)
    usual_flora = models.BooleanField(default=False)
 
    # Antibiotics Sensitivity with Severity (1-4 and Resistant)
    cloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ciprofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    lincomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    flucloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    tetracycline = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ampicillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    erythromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    roxithromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    augmentin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cotrimoxazole = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cephalexin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    dalacin_c = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    gentamycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    streptomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftriaxone = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    chloramphenicol = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nitrofurantoin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nalidixic_acid = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cefuroxime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftazidime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    pefloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)



class OccultBlood(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='occult_blood_test',null=True, blank=True)
    result = models.CharField(max_length=30, choices=[('Positive', 'Positive'), ('Negative', 'Negative')])
    comment = models.CharField(max_length=3000,null=True, blank=True)

class SputumMCS(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='sputum_mcs_test',null=True, blank=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

    # Culture yield fields with Yes/No options
    no_growth = models.BooleanField(default=False)
    e_coli = models.BooleanField(default=False)
    coliform = models.BooleanField(default=False)
    proteus = models.BooleanField(default=False)
    staph_aureus = models.BooleanField(default=False)
    pseudomonas = models.BooleanField(default=False)
    streptococcus = models.BooleanField(default=False)
    klebsiella = models.BooleanField(default=False)
    salmonella = models.BooleanField(default=False)
    str_feacalis = models.BooleanField(default=False)
    shigella = models.BooleanField(default=False)
    c_diphtheriae = models.BooleanField(default=False)
    neisseria = models.BooleanField(default=False)
    candida = models.BooleanField(default=False)
    haemophilus = models.BooleanField(default=False)
    str_pneumonia = models.BooleanField(default=False)
    str_pyogenes = models.BooleanField(default=False)
    staph_albus = models.BooleanField(default=False)
    usual_flora = models.BooleanField(default=False)
 
    # Antibiotics Sensitivity with Severity (1-4 and Resistant)
    cloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ciprofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    lincomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    flucloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    tetracycline = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ampicillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    erythromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    roxithromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    augmentin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cotrimoxazole = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cephalexin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    dalacin_c = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    gentamycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    streptomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftriaxone = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    chloramphenicol = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nitrofurantoin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nalidixic_acid = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cefuroxime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftazidime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    pefloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)


class GramStain(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='gram_stain_test',null=True, blank=True)
    # Sample Types
    urine = models.BooleanField(default=False)
    hvs = models.BooleanField("High Vaginal Swab", default=False)
    swab = models.BooleanField(default=False)
    pus = models.BooleanField(default=False)
    aspirate = models.BooleanField(default=False)
    sputum = models.BooleanField(default=False)

    # Gram Stain Findings
    gram_positive_cocci = models.BooleanField(default=False)
    gram_negative_cocci = models.BooleanField(default=False)
    gram_positive_rods = models.BooleanField(default=False)
    gram_negative_rods = models.BooleanField(default=False)
    gram_positive_clusters = models.BooleanField(default=False)
    gram_negative_clusters = models.BooleanField(default=False)
    gram_positive_chains = models.BooleanField(default=False)
    gram_negative_chains = models.BooleanField(default=False)
    other_findings = models.CharField(max_length=2000,blank=True, null=True)

    comment = models.CharField(max_length=3000,null=True, blank=True)


class ZNStain(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='zn_stain_test',null=True, blank=True)
    first_sample = models.CharField(max_length=50, blank=True, null=True,choices=[('Positive', 'Positive'), ('Negative', 'Negative')])
    second_sample = models.CharField(max_length=50, blank=True, null=True,choices=[('Positive', 'Positive'), ('Negative', 'Negative')])
    third_sample = models.CharField(max_length=50, blank=True, null=True,choices=[('Positive', 'Positive'), ('Negative', 'Negative')])
    comment = models.CharField(max_length=3000,null=True, blank=True)


class SemenAnalysis(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='semen_analysis_test',null=True, blank=True)
    time_produced = models.CharField(max_length=300, blank=True, null=True)
    time_examined = models.CharField(max_length=300, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    volume = models.CharField(max_length=10, help_text="Volume (ml)", blank=True, null=True)
    viscosity = models.CharField(max_length=50, blank=True, null=True)
    consistency = models.CharField(max_length=50, blank=True, null=True)
    motility_active = models.CharField(max_length=100, help_text="Active Motility (%)", blank=True, null=True)
    motility_moderate = models.CharField(max_length=100, help_text="Moderate Motility (%)", blank=True, null=True)
    motility_sluggish = models.CharField(max_length=100, help_text="Sluggish Motility (%)", blank=True, null=True)
    morphology_normal = models.CharField(max_length=100, help_text="Normal Morphology (%)", blank=True, null=True)
    morphology_abnormal = models.CharField(max_length=100, help_text="Abnormal Morphology (%)", blank=True, null=True)
    total_sperm_count = models.CharField(max_length=100, help_text="Total Sperm Count (x10^6/ml)", blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

    # Culture yield fields with Yes/No options
    no_growth = models.BooleanField(default=False)
    e_coli = models.BooleanField(default=False)
    coliform = models.BooleanField(default=False)
    proteus = models.BooleanField(default=False)
    staph_aureus = models.BooleanField(default=False)
    pseudomonas = models.BooleanField(default=False)
    streptococcus = models.BooleanField(default=False)
    klebsiella = models.BooleanField(default=False)
    salmonella = models.BooleanField(default=False)
    str_feacalis = models.BooleanField(default=False)
    shigella = models.BooleanField(default=False)
    c_diphtheriae = models.BooleanField(default=False)
    neisseria = models.BooleanField(default=False)
    candida = models.BooleanField(default=False)
    haemophilus = models.BooleanField(default=False)
    str_pneumonia = models.BooleanField(default=False)
    str_pyogenes = models.BooleanField(default=False)
    staph_albus = models.BooleanField(default=False)
    usual_flora = models.BooleanField(default=False)
 
    # Antibiotics Sensitivity with Severity (1-4 and Resistant)
    cloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ciprofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    lincomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    flucloxacillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    tetracycline = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ampicillin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    erythromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    roxithromycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    augmentin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cotrimoxazole = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cephalexin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    dalacin_c = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    gentamycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    streptomycin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftriaxone = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    chloramphenicol = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nitrofurantoin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    nalidixic_acid = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    cefuroxime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ceftazidime = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    ofloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)
    pefloxacin = models.CharField(max_length=10, choices=SEVERITY_CHOICES, blank=True, null=True)


class Urinalysis(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='urinalysis_test',null=True, blank=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    appearance = models.CharField(max_length=50, blank=True, null=True)
    specific_gravity = models.CharField(max_length=5, blank=True, null=True)
    ph = models.CharField(max_length=3, blank=True, null=True)
    protein = models.CharField(max_length=50, blank=True, null=True)
    glucose = models.CharField(max_length=50, blank=True, null=True)
    ketones = models.CharField(max_length=50, blank=True, null=True)
    bilirubin = models.CharField(max_length=50, blank=True, null=True)
    urobilinogen = models.CharField(max_length=50, blank=True, null=True)
    nitrites = models.CharField(max_length=50, blank=True, null=True)
    leukocyte_esterase = models.CharField(max_length=50, blank=True, null=True)
    blood = models.CharField(max_length=50, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

class Pregnancy(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='pregnancy_test',null=True, blank=True)
    result = models.CharField(max_length=100, choices=[('Positive', 'Positive'), ('Negative ', 'Negative')],null=True)
    # method = models.CharField(max_length=50, choices=[('Urine', 'Urine Test'), ('Blood', 'Blood Test')],null=True)
    # comment = models.CharField(max_length=3000,null=True, blank=True)


# SEROLOGY TEST 
class Widal(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='widal_test',null=True, blank=True)
    o_antigen_s_typhi_d = models.CharField(max_length=100, blank=True, null=True)
    o_antigen_s_paratyphi_a = models.CharField(max_length=100, blank=True, null=True)
    o_antigen_s_paratyphi_b = models.CharField(max_length=100, blank=True, null=True)
    o_antigen_s_paratyphi_c = models.CharField(max_length=100, blank=True, null=True)    
    h_antigen_s_typhi_d = models.CharField(max_length=100, blank=True, null=True)
    h_antigen_s_paratyphi_a = models.CharField(max_length=100, blank=True, null=True)
    h_antigen_s_paratyphi_b = models.CharField(max_length=100, blank=True, null=True)
    h_antigen_s_paratyphi_c = models.CharField(max_length=100, blank=True, null=True)
    diagnostic_titre = models.CharField(max_length=20, blank=True, null=True,default='> 1/80')
    mp_options = (('seen +', 'seen +'),('seen ++', 'seen ++'),('seen +++', 'seen +++'), ('not seen', 'not seen'))
    malaria_parasite=models.CharField(choices=mp_options, null=True, blank=True, max_length=100)
    comment = models.CharField(max_length=3000,null=True, blank=True)

class RheumatoidFactor(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='rheumatoid_factor_test',null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

class HPB(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='hpb_test',null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

class HCV(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='hcv_test',null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

class VDRL(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='vdrl_test',null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

class Mantoux(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='mantoux_test',null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

class AsoTitre(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='aso_titre_test',null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

class CRP(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='crp_test',null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)

class HIVScreening(models.Model):
    test = models.ForeignKey(GenericTest, on_delete=models.CASCADE, null=True, blank=True)
    test_info = models.OneToOneField(Testinfo, on_delete=models.CASCADE, related_name='hiv_test',null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=3000,null=True, blank=True)