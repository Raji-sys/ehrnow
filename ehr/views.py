from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from .models import *
from .forms import *
from .filters import *
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from pathology.models import *
from pathology.views import *
from django.utils import timezone
from datetime import timedelta
User = get_user_model()
from django.db.models import Sum
from django.http import HttpResponse
from django.conf import settings
import os
# import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, grey
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import datetime
from xhtml2pdf import pisa
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, Count



def log_anonymous_required(view_function, redirect_to=None):
    if redirect_to is None:
        redirect_to = '/'
    return user_passes_test(lambda u: not u.is_authenticated, login_url=redirect_to)(view_function)

# Mixins
class RecordRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='record').exists()

class RevenueRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='revenue').exists()

class NurseRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='nurse').exists()

class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='doctor').exists()

class DoctorNurseRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='doctor').exists() or self.request.user.groups.filter(name='nurse').exists() 


class PharmacyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='pharmacist').exists()

class RadiologyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='radiologist').exists()

class PhysioRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='physiotherapist').exists()

class AuditorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='auditor').exists()


@login_required
def fetch_resources(uri, rel):
    """
    Handles fetching static and media resources when generating the PDF.
    """
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT,
                            uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.MEDIA_ROOT,
                            uri.replace(settings.MEDIA_URL, ""))
    return path


@method_decorator(log_anonymous_required, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('index')
        else:
            return reverse_lazy('profile_details', args=[self.request.user.username])


def reg_anonymous_required(view_function, redirect_to=None):
    if redirect_to is None:
        redirect_to = '/'
    return user_passes_test(lambda u: not u.is_authenticated or u.is_superuser, login_url=redirect_to)(view_function)


@method_decorator(reg_anonymous_required, name='dispatch')
class UserRegistrationView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
        if form.is_valid():
            response = super().form_valid(form)
            user = User.objects.get(username=form.cleaned_data['username'])
            profile_instance = Profile(user=user)
            profile_instance.save()
            messages.success(
                self.request, f"Registration for: {user.get_full_name()} was successful")
            return response
        else:
            print("Form errors:", form.errors)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('get_started')


@method_decorator(login_required(login_url='login'), name='dispatch')
class DocumentationView(UpdateView):
    model = User
    template_name = 'doc.html'
    form_class = UserForm
    success_url = reverse_lazy('stafflist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profileform'] = ProfileForm(instance=self.object.profile)
        return context

    def form_valid(self, form):
        userform = UserForm(self.request.POST, instance=self.object)
        profileform = ProfileForm(self.request.POST, instance=self.object.profile)

        if userform.is_valid() and profileform.is_valid():
            userform.save()
            profileform.save()
            messages.success(
                self.request, f'Documentation successful!{self.request.user.last_name}')
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(
                self.request, 'Please correct the errors to proceed')
            return self.form_invalid(form)
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class UpdateUserView(UpdateView):
    model = User
    template_name = 'update_user.html'
    form_class = UserForm

    def get_success_url(self):
        messages.success(
            self.request, 'Staff Information Updated Successfully')
        return self.object.profile.get_absolute_url()

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'error updating staff information')
        return self.render_to_response(self.get_context_data(form=form))



@method_decorator(login_required(login_url='login'), name='dispatch')
class UpdateProfileView(UpdateView):
    model = Profile
    template_name = 'update_profile.html'
    form_class = ProfileForm

    def get_success_url(self):
        messages.success(self.request, 'Staff Information Updated Successfully')
        return self.object.get_absolute_url()
    
    def form_valid(self, form):
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'error updating staff information')
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfileDetailView(DetailView):
    template_name = 'profile_details.html'
    model = Profile

    def get_object(self, queryset=None):
        if self.request.user.is_superuser:
            username_from_url = self.kwargs.get('username')
            user = get_object_or_404(User, username=username_from_url)
        else:
            user = self.request.user
        return get_object_or_404(Profile, user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = context['object']

        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class StaffListView(ListView):
    model = Profile
    template_name = "stafflist.html"
    context_object_name = 'profiles'
    paginate_by = 10

    def get_queryset(self):
        profiles = super().get_queryset().order_by('-user_id')
        staff_filter = StaffFilter(self.request.GET, queryset=profiles)
        return staff_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_profiles = self.get_queryset().count()
        context['staffFilter'] = StaffFilter(self.request.GET, queryset=self.get_queryset())
        context['total_profiles'] = total_profiles
        return context
    
class IndexView(TemplateView):
    template_name = "index.html"
    # template_name = "get_started.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class GetStartedView(TemplateView):
    template_name = "get_started.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class StaffDashboardView(TemplateView):
    template_name = "staff.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class MedicalRecordView(RecordRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/medical_record.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class PatientMovementView(TemplateView):
    template_name = "ehr/record/patient_moves.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class AppointmentDashboardView(TemplateView):
    template_name = "ehr/record/appt_dashboard.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class RevenueView(RevenueRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/revenue.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class RevenueRecordView(TemplateView):
    template_name = "ehr/revenue/record_revenue.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class NursingView(NurseRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/nursing.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicDashView(DoctorRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/clinic_list.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicView(TemplateView):
    template_name = "ehr/record/clinic.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicBaseView(TemplateView):
    template_name = "ehr/record/clinic.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class RadiologyView(RadiologyRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/radiology.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class PharmacyView(PharmacyRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/pharmacy.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class PhysioView(PhysioRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/physio.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class TheatreView(DoctorNurseRequiredMixin, TemplateView):
    template_name = "ehr/dashboard/theatre.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class WardView(DoctorNurseRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/ward_list.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class AuditView(AuditorRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/audit.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class ServiceView(TemplateView):
    template_name = "ehr/dashboard/service.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class AEClinicDetailView(TemplateView):
    template_name = 'ehr/clinic/ae_details.html'


@method_decorator(login_required(login_url='login'), name='dispatch')
class SOPDClinicDetailView(TemplateView):
    template_name = 'ehr/clinic/sopd_details.html'

@method_decorator(login_required(login_url='login'), name='dispatch')
class MaleWardDetailView(TemplateView):
    template_name = 'ehr/ward/male_ward_details.html'

@method_decorator(login_required(login_url='login'), name='dispatch')
class FemaleWardDetailView(TemplateView):
    template_name = 'ehr/ward/female_ward_details.html'

@method_decorator(login_required(login_url='login'), name='dispatch')
class ChildrensWardDetailView(TemplateView):
    template_name = 'ehr/ward/childrens_ward_details.html'

@method_decorator(login_required(login_url='login'), name='dispatch')
class ICUDetailView(TemplateView):
    template_name = 'ehr/ward/icu_details.html'


#1 Patient create
class PatientCreateView(RecordRequiredMixin, CreateView):
    model = PatientData
    form_class = PatientForm
    template_name = 'ehr/record/new_patient.html'
    success_url = reverse_lazy("medical_record")

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient = form.save()
        PatientHandover.objects.create(patient=patient, clinic='A & E', status='waiting for payment')
        messages.success(self.request, 'Patient registered successfully')
        return super().form_valid(form)


class UpdatePatientView(UpdateView):
    model = PatientData
    template_name = 'ehr/record/update_patient.html'
    form_class = PatientForm
    success_url =reverse_lazy('patient_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Patient Information Updated Successfully')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating patient information')
        return self.render_to_response(self.get_context_data(form=form))


class PatientListView(ListView):
    model=PatientData
    template_name='ehr/record/patient_list.html'
    context_object_name='patients'
    paginate_by = 10

    def get_queryset(self):
        patients = super().get_queryset().order_by('-file_no')
        patient_filter = PatientFilter(self.request.GET, queryset=patients)
        return patient_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_patient = self.get_queryset().count()
        context['patientFilter'] = PatientFilter(self.request.GET, queryset=self.get_queryset())
        context['total_patient'] = total_patient
        return context


class PatientReportView(ListView):
    model = PatientData
    template_name = 'ehr/report/patient_report.html'
    context_object_name = 'patients'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-updated')
        self.filterset = PatientReportFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patientReportFilter'] = self.filterset
        context['total_patient'] = PatientData.objects.count()
        context['filtered_count'] = self.filterset.qs.count()
        return context


@login_required
def patient_report_pdf(request):
    ndate = datetime.datetime.now()
    filename = ndate.strftime('on__%d/%m/%Y__at__%I.%M%p.pdf')
    f = PatientReportFilter(request.GET, queryset=PatientData.objects.all()).qs
    result = ""
    result2 = ""
    result3 = ""
    for key, value in request.GET.items():
        if value:
            result += f"{value.upper()} "
            result2 += f"Generated on: {ndate.strftime('%d-%B-%Y : %I:%M %p')}" 
            result3 += f"By: {request.user.username.upper()}"

    context = {'f': f, 'pagesize': 'A4',
               'orientation': 'landscape', 'result': result,'result2':result2,'result3':result3}
    response = HttpResponse(content_type='application/pdf',
                            headers={'Content-Disposition': f'filename="Report__{filename}"'})

    buffer = BytesIO()

    pisa_status = pisa.CreatePDF(get_template('ehr/record/patient_report_pdf.html').render(
        context), dest=buffer, encoding='utf-8', link_callback=fetch_resources)

    if not pisa_status.err:
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    return HttpResponse('Error generating PDF', status=500)


class PatientHandoverReportView(ListView):
    model = PatientHandover
    template_name = 'ehr/clinic/report.html'
    context_object_name = 'handovers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-updated')
        self.filterset = PatientHandoverFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patientHandoverFilter'] = self.filterset
        context['total_patient'] = PatientData.objects.count()
        context['filtered_count'] = self.filterset.qs.count()
        return context
    

@login_required
def clinic_handover_pdf(request):
    ndate = datetime.datetime.now()
    filename = ndate.strftime('on__%d/%m/%Y__at__%I.%M%p.pdf')
    f = PatientHandoverFilter(request.GET, queryset=PatientHandover.objects.all()).qs
    patient = f.first().patient if f.exists() else None
    result = ""
    result2 = ""
    result3 = ""
    for key, value in request.GET.items():
        if value:
            result += f"{value.upper()} "
            result2 += f"Generated on: {ndate.strftime('%d-%B-%Y : %I:%M %p')}" 
            result3 += f"By: {request.user.username.upper()}"

    context = {'f': f, 'pagesize': 'A4','patient':patient,
               'orientation': 'landscape', 'result': result,'result2':result2,'result3':result3}
    response = HttpResponse(content_type='application/pdf',
                            headers={'Content-Disposition': f'filename="Report__{filename}"'})

    buffer = BytesIO()

    pisa_status = pisa.CreatePDF(get_template('ehr/clinic/clinic_handover_pdf.html').render(
        context), dest=buffer, encoding='utf-8', link_callback=fetch_resources)

    if not pisa_status.err:
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    return HttpResponse('Error generating PDF', status=500)


@method_decorator(login_required(login_url='login'), name='dispatch')
class PatientStatsView(TemplateView):
    template_name = 'ehr/record/stats.html'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        pc = PatientData.objects.all().count()
        gender_counts = PatientData.objects.values('gender').annotate(pc=Count('id'))
        geo_counts = PatientData.objects.values('zone').annotate(pc=Count('id'))
        state_counts = PatientData.objects.values('state').annotate(pc=Count('id'))
        lga_counts = PatientData.objects.values('lga').annotate(pc=Count('id'))
        religion_counts = PatientData.objects.values('religion').annotate(pc=Count('id'))
        marital_status_counts = PatientData.objects.values('marital_status').annotate(pc=Count('id'))
        nationality_counts = PatientData.objects.values('nationality').annotate(pc=Count('id'))
        occupation_counts = PatientData.objects.values('occupation').annotate(pc=Count('id'))
        role_in_occupation_counts = PatientData.objects.values('role_in_occupation').annotate(pc=Count('id'))
        address_counts = PatientData.objects.values('address').annotate(pc=Count('id'))
        context['pc'] = pc
        context['gender_counts'] = gender_counts
        context['geo_counts'] = geo_counts
        context['state_counts'] = state_counts
        context['lga_counts'] = lga_counts
        context['religion_counts'] = religion_counts
        context['marital_status_counts'] = marital_status_counts
        context['nationality_counts'] = nationality_counts
        context['occupation_counts'] = occupation_counts
        context['role_in_occupation_counts'] = role_in_occupation_counts
        context['address_counts'] = address_counts
        return context
    
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class PatientFolderView(DetailView):
    template_name = 'ehr/record/patient_folder.html'
    model = PatientData
 
    def get_object(self, queryset=None):
        obj = PatientData.objects.get(file_no=self.kwargs['file_no'])
        user = self.request.user
        allowed_groups = ['nurse', 'doctor', 'record', 'pathologist', 'pharmacist']

        if not any(group in user.groups.values_list('name', flat=True) for group in allowed_groups):
            raise PermissionDenied()
        return obj
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        context['patient'] = patient
        context['vitals'] = patient.vital_signs.all().order_by('-updated')
        context['payments'] = patient.patient_payments.all().order_by('-updated')
        context['clinical_notes'] = patient.clinical_notes.all().order_by('-updated')
        context['prescribed_drugs'] = patient.prescribed_drugs.all().order_by('-updated')
        context['hematology_results']=patient.hematology_result.all().order_by('-created')
        context['chempath_results']=patient.chemical_pathology_results.all().order_by('-created')
        context['micro_results']=patient.microbiology_results.all().order_by('-created')
        context['serology_results']=patient.serology_results.all().order_by('-created')
            # context['general_results']=patient.general_results.all().order_by('-created')
        context['radiology_results'] = patient.radiology_results.all().order_by('-updated')
        context['admission_info'] = patient.admission_info.all().order_by('-updated')
        context['ward_vital_signs'] = patient.ward_vital_signs.all().order_by('-updated')
        context['ward_medication'] = patient.ward_medication.all().order_by('-updated')
        context['ward_clinical_notes'] = patient.ward_clinical_notes.all().order_by('-updated')
        context['theatre_bookings'] = patient.theatre_bookings.all().order_by('-updated')
        context['theatre_notes'] = patient.theatre_notes.all().order_by('-updated')
        context['surgery_bill'] = patient.surgery_bill.all().order_by('-created')
        context['bills'] = Bill.objects.filter(patient=self.object).order_by('-created')
        radiology_results = patient.radiology_results.all().order_by('-updated')
        context['radiology_results'] = radiology_results
        # Calculate total worth only for paid transactions
        paid_transactions = patient.patient_payments.filter(status=True)
        paid_transactions_count = paid_transactions.count()

        context['paid_transactions_count'] = paid_transactions_count

        # Calculate the total amount
        total_amount = paid_transactions.aggregate(total_amount=Sum('price'))['total_amount'] or 0
        context['total_amount'] = total_amount    
        return context
   
# 2. FollowUpVisitCreateView
class FollowUpVisitCreateView(RecordRequiredMixin, CreateView):
    model = FollowUpVisit
    form_class = VisitForm
    template_name = 'ehr/record/follow_up.html'
    success_url = reverse_lazy("medical_record")

    def get_patient(self):
        file_no = self.kwargs.get('file_no')
        return PatientData.objects.get(file_no=file_no)

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient = self.get_patient()
        visit = form.save(commit=False)
        visit.patient = patient
        visit.save()
        clinic = form.cleaned_data['clinic']

        # Create or update PatientHandover
        PatientHandover.objects.update_or_create(
            patient=patient,
            clinic=clinic,
            defaults={'status': 'f waiting for payment','room':None}
        )
        messages.success(self.request, 'Follow-up visit created successfully')
        return redirect(self.success_url)

class FollowUpListView(ListView):
    model=PatientData
    template_name='ehr/record/follow_up_list.html'
    context_object_name='patients'
    paginate_by = 10

    def get_queryset(self):
        patients = super().get_queryset().order_by('-updated')
        patient_filter = PatientFilter(self.request.GET, queryset=patients)
        return patient_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patientFilter'] = PatientFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PaypointDashboardView(RevenueRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/revenue/paypoint_dash.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status__in=['waiting for payment'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PaypointFollowUpDashboardView(RevenueRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/revenue/follow_up_pay_dash.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(
            status='f waiting for payment',
            patient__follow_up__isnull=False
        ).distinct()

    
class PaypointView(RevenueRequiredMixin, CreateView):
    model=Paypoint
    template_name = 'ehr/revenue/paypoint.html'
    form_class = PayForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        handover = patient.handovers.filter(clinic='A & E', status='waiting for payment').first()
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))


        if handover:
            context['patient'] = patient
            context['handover'] = handover
            service = MedicalRecord.objects.get(name='new registration')
            context['service'] = service
        else:
            # Handle the case where no handover object is found
            pass

        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        handover = patient.handovers.filter(clinic='A & E', status='waiting for payment').first()
        if handover:
            payment = form.save(commit=False)
            payment.patient = patient
            payment.status = True
            service = MedicalRecord.objects.get(name='new registration')
            payment.service = service.name
            payment.price = service.price
            payment.save()

            # Update handover status to 'waiting_for_vital_signs'
            handover.status = 'waiting for vital signs'
            handover.save()
            messages.success(self.request, 'Payment successful. Patient handed over for vital signs.')
        return super().form_valid(form) 


class PaypointFollowUpView(RevenueRequiredMixin, CreateView):
    model=Paypoint
    template_name = 'ehr/revenue/paypoint_follow_up.html'
    form_class = PayForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_no = self.kwargs.get('file_no')
        context['patient'] = get_object_or_404(PatientData, file_no=file_no)

        service_name = 'follow up'
        service = MedicalRecord.objects.get(name=service_name)
        context['service_name'] = service.name
        context['service_price'] = service.price
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)        
        handover = patient.handovers.filter(status='f waiting for payment').first()
        if handover:
            payment = form.save(commit=False)
            payment.patient = patient
            payment.status = True
            service = MedicalRecord.objects.get(name='follow up')
            payment.service = service.name
            payment.price = service.price
            payment.save()

            handover.status = 'waiting for vital signs'
            handover.save()
            messages.success(self.request, 'Payment successful. Patient handed over for vitals.')        
        return super().form_valid(form)


class VitalSignCreateView(NurseRequiredMixin,CreateView):
    model = VitalSigns
    form_class = VitalSignsForm
    template_name = 'ehr/nurse/vital_signs.html'
    success_url = reverse_lazy('nursing')

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        # Update handover status to 'waiting_for_consultation'
        patient_handovers = PatientHandover.objects.filter(patient=patient_data)
        for patient_handover in patient_handovers:
            patient_handover.status = 'waiting for consultation'
            patient_handover.clinic = patient_handover.clinic
            patient_handover.room = form.cleaned_data['handover_room']
            patient_handover.save()

        # If there are no existing handovers, create a new one
        if not patient_handovers.exists():
            PatientHandover.objects.create(patient=patient_data, status='waiting for consultation')
        messages.success(self.request, 'Vitals taken, Patient handed over for consultation')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context

    
###BASE CLINIC###
class ClinicListView(DoctorRequiredMixin, ListView):
    model = PatientHandover
    context_object_name = 'handovers'

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {
            'status': self.status_filter,
            'clinic': self.clinic_filter,
            'updated__gte': timezone.now() - timedelta(days=1), 
            # 'updated_at__gte': timezone.now() - timedelta(hours=12)
        }
        if self.room_filter is not None:
            filters['room'] = self.room_filter
        filtered_queryset = queryset.filter(**filters)
        return filtered_queryset.order_by('-updated')


class AENursingDeskView(ClinicListView):
    template_name = 'ehr/nurse/ae_nursing_desk.html'
    status_filter = 'waiting for vital signs'
    clinic_filter = "A & E"
    room_filter = None


class SOPDNursingDeskView(ClinicListView):
    template_name = 'ehr/nurse/sopd_nursing_desk.html'
    status_filter = 'waiting for vital signs'
    clinic_filter = "SOPD"
    room_filter = None

class AEConsultationWaitRoomView(ClinicListView):
    template_name = 'ehr/clinic/ae_list.html'
    status_filter = 'waiting for consultation'
    clinic_filter = "A & E"
    room_filter = None

class AERoom1View(ClinicListView):
    template_name = 'ehr/clinic/ae_room1.html'
    status_filter = 'waiting for consultation'
    clinic_filter = "A & E"
    room_filter = 'ROOM 1'


class AERoom2View(ClinicListView):
    template_name = 'ehr/clinic/ae_room2.html'
    status_filter = 'waiting for consultation'
    clinic_filter = "A & E"
    room_filter = 'ROOM 2'


class SOPDConsultationWaitRoomView(ClinicListView):
    template_name = 'ehr/clinic/sopd_list.html'
    status_filter = 'waiting for consultation'
    clinic_filter = "SOPD"
    room_filter = None

class SOPDRoom1View(ClinicListView):
    template_name = 'ehr/clinic/sopd_room1.html'
    status_filter = 'waiting for consultation'
    clinic_filter = "SOPD"
    room_filter = 'ROOM 1'


class SOPDRoom2View(ClinicListView):
    template_name = 'ehr/clinic/sopd_room2.html'
    status_filter = 'waiting for consultation'
    clinic_filter = "SOPD"
    room_filter = 'ROOM 2'


@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicalNoteCreateView(CreateView, DoctorRequiredMixin):
    model = ClinicalNote
    form_class = ClinicalNoteForm
    template_name = 'ehr/doctor/clinical_note.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        # Update handover status based on the needs_review value
        patient_handovers = PatientHandover.objects.filter(patient=patient_data)
        for patient_handover in patient_handovers:
            if form.instance.needs_review:
                patient_handover.status = 'awaiting review'
            else:
                patient_handover.status = 'seen'
            patient_handover.clinic = patient_handover.clinic
            patient_handover.save()

        # If there are no existing handovers, create a new one
        if not patient_handovers.exists():
            PatientHandover.objects.create(
                patient=patient_data,
                status='awaiting review' if form.instance.needs_review else 'seen'
            )

        return super().form_valid(form)


    def test_func(self):
        allowed_groups = ['doctor']
        return any(group in self.request.user.groups.values_list('name', flat=True) for group in allowed_groups)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context

    def get_success_url(self):
        messages.success(self.request, 'PATIENT SEEN.')
        return self.object.patient.get_absolute_url()


class ClinicalNoteUpdateView(UpdateView):
    model = ClinicalNote
    template_name = 'ehr/doctor/update_clinical_note.html'
    form_class = ClinicalNoteUpdateForm
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error')
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        messages.success(self.request, 'CLINICAL NOTE UPDATED')
        return self.object.patient.get_absolute_url()


class AEConsultationFinishView(ClinicListView):
    template_name = 'ehr/doctor/ae_patient_seen.html'
    status_filter = 'seen'
    clinic_filter = 'A & E'
    room_filter = None


class AEAwaitingReviewView(ClinicListView):
    template_name = 'ehr/doctor/ae_review_patient.html'
    status_filter = 'awaiting review'
    clinic_filter = 'A & E'
    room_filter = None


class SOPDConsultationFinishView(ClinicListView):
    template_name = 'ehr/doctor/sopd_patient_seen.html'
    status_filter = 'seen'
    clinic_filter = 'SOPD'
    room_filter = None

class SOPDAwaitingReviewView(ClinicListView):
    template_name = 'ehr/doctor/sopd_review_patient.html'
    status_filter = 'awaiting review'
    clinic_filter = 'SOPD'
    room_filter = None
    

class AppointmentCreateView(RecordRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'ehr/record/new_appointment.html'
    success_url = reverse_lazy("appointments")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        self.object = form.save()
        messages.success(self.request, 'APPOINTMENT ADDED')
        return super().form_valid(form)


class AppointmentUpdateView(UpdateView):
    model = Appointment
    template_name = 'ehr/record/update_appt.html'
    form_class = AppointmentForm
    success_url = reverse_lazy("appointments")

    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Appointment Updated Successfully')
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating appointment information')
        return self.render_to_response(self.get_context_data(form=form))


class NewAppointmentListView(ListView):
    model=PatientData
    template_name='ehr/record/new_appt_list.html'
    context_object_name='patients'
    paginate_by = 10

    def get_queryset(self):
        patients = super().get_queryset().order_by('-updated')
        patient_filter = PatientFilter(self.request.GET, queryset=patients)
        return patient_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patientFilter'] = PatientFilter(self.request.GET, queryset=self.get_queryset())
        return context
    

class AppointmentListView(ListView):
    model=Appointment
    template_name='ehr/record/appointment.html'
    context_object_name='appointments'
    paginate_by = 10

    def get_queryset(self):
        appointment = super().get_queryset().order_by('-updated_at')
        appointment_filter = AppointmentFilter(self.request.GET, queryset=appointment)
        return appointment_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointmentFilter'] = AppointmentFilter(self.request.GET, queryset=self.get_queryset())
        return context


class HospitalServicesListView(TemplateView):
    template_name='ehr/dashboard/services.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medical_record'] = MedicalRecord.objects.all()
        context['hematology'] = HematologyTest.objects.all()
        context['services'] = Services.objects.all()
        return context


class ServiceCreateView(RevenueRequiredMixin, CreateView):
    model = Services
    form_class = ServiceForm
    template_name = 'ehr/revenue/new_service.html'
    success_url = reverse_lazy("hospital_services")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'SERVICE ADDED')
        return super().form_valid(form)

 
class ServiceUpdateView(UpdateView):
    model = Services
    template_name = 'ehr/revenue/update_service.html'
    form_class = ServiceForm
    success_url = reverse_lazy("service_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Service Updated Successfully')
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating service information')
        return self.render_to_response(self.get_context_data(form=form))


class ServiceListView(ListView):
    model=Services
    template_name='ehr/revenue/general_services.html'
    context_object_name='services'
    paginate_by = 10

    def get_queryset(self):
        type = super().get_queryset().order_by('-type')
        service_filter = ServiceFilter(self.request.GET, queryset=type)
        return service_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_services = self.get_queryset().count()
        context['serviceFilter'] = ServiceFilter(self.request.GET, queryset=self.get_queryset())
        context['total_services'] = total_services
        return context


class PayCreateView(RevenueRequiredMixin, CreateView):
        model = Paypoint
        form_class = PayForm
        template_name = 'ehr/revenue/new_pay.html'
        success_url = reverse_lazy("pay_list")

        def form_valid(self, form):
            form.instance.user = self.request.user
            messages.success(self.request, 'PAYMENT ADDED')
            return super().form_valid(form)

 
class PayUpdateView(UpdateView):
    model = Paypoint
    template_name = 'ehr/revenue/update_pay.html'
    form_class = PayUpdateForm

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paypoint = self.get_object()
        context['patient'] = paypoint.patient
        context['service'] = paypoint.service
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        paypoint = form.save()
        messages.success(self.request, 'Payment Successfully Updated')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating payment information')
        return self.render_to_response(self.get_context_data(form=form))


class PayListView(ListView):
    model=Paypoint
    template_name='ehr/revenue/transaction.html'
    context_object_name='pays'
    paginate_by = 10

    def get_queryset(self):
        updated = super().get_queryset().filter(status=True).order_by('-updated')
        pay_filter = PayFilter(self.request.GET, queryset=updated)
        return pay_filter.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()
        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['payFilter'] = PayFilter(self.request.GET, queryset=self.get_queryset())
        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        return context    
    
# @login_required
# def receipt_pdf(request):
#     ndate = datetime.datetime.now()
#     filename = ndate.strftime('on__%d/%m/%Y__at__%I.%M%p.pdf')
#     f = PayFilter(request.GET, queryset=Paypoint.objects.all()).qs
#     patient = f.first().patient if f.exists() else None
#     result = ""
#     for key, value in request.GET.items():
#         if value:
#             result += f" {value.upper()}<br>Generated on: {ndate.strftime('%d-%B-%Y at %I:%M %p')}</br>By: {request.user.username.upper()}"

#     context = {'f': f, 'pagesize': 'A4','patient':patient,
#                'orientation': 'landscape', 'result': result}
#     response = HttpResponse(content_type='application/pdf',
#                             headers={'Content-Disposition': f'filename="Receipt__{filename}"'})

#     buffer = BytesIO()

#     pisa_status = pisa.CreatePDF(get_template('ehr/revenue/receipt_pdf.html').render(
#         context), dest=buffer, encoding='utf-8', link_callback=fetch_resources)

#     if not pisa_status.err:
#         pdf = buffer.getvalue()
#         buffer.close()
#         response.write(pdf)
#         return response
#     return HttpResponse('Error generating PDF', status=500)
    

def format_currency(amount):
    if amount is None:
        return "N0.00"
    return f"N{amount:,.2f}"

@login_required
def receipt_pdf(request):
    # Get the queryset
    f = PayFilter(request.GET, queryset=Paypoint.objects.all()).qs
    
    # Get the patient from the first Paypoint object
    patient = f.first().patient if f.exists() else None

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=(3*inch, 11*inch))  # 3 inches wide, 11 inches long

    # Try to register custom fonts, fall back to standard fonts if not available
    try:
        pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
        pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
        font_name = 'Vera'
        font_bold = 'VeraBd'
    except:
        font_name = 'Helvetica'
        font_bold = 'Helvetica-Bold'

    # Start drawing from the top of the page
    y = 10.5*inch

    # Try to draw logo if available
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', '5.png')
    if os.path.exists(logo_path):
        p.drawInlineImage(logo_path, 0.75*inch, y - 0.5*inch, width=1.5*inch, height=0.5*inch)
        y -= 0.7*inch
    else:
        y -= 0.2*inch  # Adjust spacing if no logo

    # Draw the header
    p.setFont(font_bold, 12)
    p.drawCentredString(1.5*inch, y, "PAYMENT RECEIPT")
    y -= 0.3*inch

    # Draw a line
    p.setStrokeColor(grey)
    p.line(0.25*inch, y, 2.75*inch, y)
    y -= 0.2*inch

    # Draw patient info
    p.setFont(font_name, 8)
    if patient:
        p.drawString(0.25*inch, y, f"Patient: {patient}")
        y -= 0.15*inch
        p.drawString(0.25*inch, y, f"File No: {patient.file_no}")
        y -= 0.2*inch

    # Draw a line
    p.line(0.25*inch, y, 2.75*inch, y)
    y -= 0.2*inch

    # Draw column headers
    p.setFont(font_bold, 8)
    p.drawString(0.25*inch, y, "Service")
    p.drawString(1.75*inch, y, "Price")
    p.drawString(2.25*inch, y, "Date")
    y -= 0.15*inch

    # Draw a line
    p.line(0.25*inch, y, 2.75*inch, y)
    y -= 0.1*inch

    # Draw payment details
    p.setFont(font_name, 8)
    total = 0
    for payment in f:
        if y < 1*inch:  # If we're near the bottom of the page, start a new page
            p.showPage()
            p.setFont(font_name, 8)
            y = 10.5*inch

        p.drawString(0.25*inch, y, str(payment.service)[:20])  # Truncate long service names
        p.drawRightString(2.15*inch, y, format_currency(payment.price))
        p.drawString(2.25*inch, y, payment.updated.strftime("%d/%m"))
        y -= 0.15*inch
        total += payment.price or 0  # Use 0 if price is None

    # Draw a line
    y -= 0.1*inch
    p.setStrokeColor(black)
    p.line(0.25*inch, y, 2.75*inch, y)
    y -= 0.2*inch

    # Draw total
    p.setFont(font_bold, 10)
    p.drawString(0.25*inch, y, "Total:")
    p.drawRightString(2.75*inch, y, format_currency(total))

    # Draw footer
    y -= 0.4*inch
    p.setFont(font_name, 7)
    p.drawCentredString(1.5*inch, y, f"Generated: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}")
    y -= 0.15*inch
    p.drawCentredString(1.5*inch, y, f"By: {request.user.username.upper()}")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


class PathologyPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/pathology_pay_list.html'
    # context_object_name = 'hematology_pays'
    paginate_by = 10

    def get_queryset(self):
        # We'll handle this in get_context_data
        return Paypoint.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hematology_pays = Paypoint.objects.filter(hematology_result_payment__isnull=False).order_by('-updated')
        chempath_pays = Paypoint.objects.filter(chempath_result_payment__isnull=False).order_by('-updated')
        micro_pays = Paypoint.objects.filter(micro_result_payment__isnull=False).order_by('-updated')
        serology_pays = Paypoint.objects.filter(serology_result_payment__isnull=False).order_by('-updated')
        # general_pays = Paypoint.objects.filter(general_result_payment__isnull=False).order_by('-updated')

        hema_pay_total = hematology_pays.count()
        hema_paid_transactions = hematology_pays.filter(status=True)
        hema_total_worth = hema_paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        chem_pay_total = chempath_pays.count()
        chem_paid_transactions = chempath_pays.filter(status=True)
        chem_total_worth = chem_paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        micro_pay_total = micro_pays.count()
        micro_paid_transactions = micro_pays.filter(status=True)
        micro_total_worth = micro_paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        serology_pay_total = serology_pays.count()
        serology_paid_transactions = serology_pays.filter(status=True)
        serology_total_worth = serology_paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        # general_pay_total = general_pays.count()
        # general_paid_transactions = general_pays.filter(status=True)
        # general_total_worth = general_paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        # Combined total worth
        combined_total_worth = hema_total_worth + chem_total_worth + micro_total_worth + serology_total_worth

        context['hematology_pays'] = hematology_pays
        context['chempath_pays'] = chempath_pays
        context['micro_pays'] = micro_pays
        context['serology_pays'] = serology_pays
        # context['general_pays'] = general_pays

        context['hema_pay_total'] = hema_pay_total
        context['chem_pay_total'] = chem_pay_total
        context['micro_pay_total'] = micro_pay_total
        context['serology_pay_total'] = serology_pay_total
        # context['general_pay_total'] = general_pay_total

        context['hema_total_worth'] = hema_total_worth
        context['chem_total_worth'] = chem_total_worth
        context['micro_total_worth'] = micro_total_worth
        context['serology_total_worth'] = serology_total_worth
        # context['general_total_worth'] = general_total_worth
        
        context['combined_total_worth'] = combined_total_worth
        return context  


class RadiologyPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/radiology_pay_list.html'
    context_object_name = 'radiology_pays'
    paginate_by = 10

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        return Paypoint.objects.filter(radiology_result_payment__isnull=False).order_by('-updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        return context  


class PharmPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/pharm_pay_list.html'
    context_object_name = 'pharm_pays'
    paginate_by = 10

    def get_queryset(self):
        return Paypoint.objects.filter(pharm_payment__isnull=False).order_by('-updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        # Calculate total worth only for paid transactions
        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        return context  
    

class AdmissionCreateView(RevenueRequiredMixin, CreateView):
    model = Admission
    form_class = AdmissionForm
    template_name = 'ehr/ward/new_admission.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        self.object = form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'PATIENT ADMITTED')
        return self.object.patient.get_absolute_url()

 
class AdmissionUpdateView(UpdateView):
    model = Admission
    template_name = 'ehr/ward/update_admission.html'
    form_class = AdmissionUpdateForm
    success_url = reverse_lazy("ward_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'PATIENT RECEIVED')
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error')
        return self.render_to_response(self.get_context_data(form=form))


class AdmissionListView(ListView):
    model=Admission
    template_name='ehr/ward/admission_list.html'
    context_object_name='admissions'
    paginate_by = 10

    def get_queryset(self):
        updated = super().get_queryset().order_by('-updated')
        admission_filter = AdmissionFilter(self.request.GET, queryset=updated)
        return admission_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_admissions = self.get_queryset().count()
        context['admissionFilter'] = AdmissionFilter(self.request.GET, queryset=self.get_queryset())
        context['total_admission'] = total_admissions
        return context
    

###BASE WARD###
class WardListView(DoctorRequiredMixin, ListView):
    model = Admission
    context_object_name = 'admissions'

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {
            'admit': self.admit_filter,
            'accept': self.accept_filter,
            'ward': self.ward_filter,
            # 'created_at__gte': timezone.now() - timedelta(days=1), 
        }
        filtered_queryset = queryset.filter(**filters)
        return filtered_queryset.order_by('-updated')


class ICUWaitListView(WardListView):
    template_name = 'ehr/ward/icu_wait_list.html'
    ward_filter = 'ICU'
    admit_filter = True
    accept_filter = False


class ICUView(WardListView):
    template_name = 'ehr/ward/icu.html'
    ward_filter = 'ICU'
    admit_filter = True
    accept_filter = True


class MaleWardWaitListView(WardListView):
    template_name = 'ehr/ward/male_ward_wait_list.html'
    ward_filter = 'MALE WARD'
    admit_filter = True
    accept_filter=False


class MaleWardView(WardListView):
    template_name = 'ehr/ward/male_ward.html'
    ward_filter = 'MALE WARD'
    admit_filter = True
    accept_filter = True


class FemaleWardWaitListView(WardListView):
    template_name = 'ehr/ward/female_ward_wait_list.html'
    ward_filter = 'FEMALE WARD'
    admit_filter = True
    accept_filter= False


class FemaleWardView(WardListView):
    template_name = 'ehr/ward/female_ward.html'
    ward_filter = 'FEMALE WARD'
    admit_filter = True
    accept_filter= True


class ChildrensWardWaitListView(WardListView):
    template_name = 'ehr/ward/childrens_ward_wait_list.html'
    ward_filter = 'CHILDRENS WARD'
    admit_filter = True
    accept_filter=False


class ChildrensWardView(WardListView):
    template_name = 'ehr/ward/childrens_ward.html'
    ward_filter = 'CHILDRENS WARD'
    admit_filter = True
    accept_filter= True


class WardVitalSignCreateView(NurseRequiredMixin,CreateView):
    model = WardVitalSigns
    form_class = WardVitalSignsForm
    template_name = 'ehr/ward/ward_vital_signs.html'
    success_url = reverse_lazy('ward_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        messages.success(self.request, 'Vitals taken')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context


class WardMedicationCreateView(NurseRequiredMixin,CreateView):
    model = WardMedication
    form_class = WardMedicationForm
    template_name = 'ehr/ward/ward_medication.html'
    success_url = reverse_lazy('ward_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        messages.success(self.request, 'Medication Given')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context


class WardNotesCreateView(NurseRequiredMixin,CreateView):
    model = WardClinicalNote
    form_class = WardNotesForm
    template_name = 'ehr/ward/ward_notes.html'
    success_url = reverse_lazy('ward_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        messages.success(self.request, 'Notes Taken')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context


class TheatreBookingCreateView(DoctorRequiredMixin, CreateView):
        model = TheatreBooking
        form_class = TheatreBookingForm
        template_name = 'ehr/theatre/book_theatre.html'

        def form_valid(self, form):
            form.instance.user = self.request.user
            form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
            self.object = form.save()
            return super().form_valid(form)
        
        def get_success_url(self):
            messages.success(self.request, 'PATIENT BOOKED FOR SURGERY')
            return self.object.patient.get_absolute_url()


class TheatreBookingUpdateView(DoctorRequiredMixin,UpdateView):
    model = TheatreBooking
    template_name = 'ehr/theatre/update_theatre_booking.html'
    form_class = TheatreBookingForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Appointment Updated Successfully')
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating booking information')
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        messages.success(self.request, 'PATIENT THEATRE BOOKING UPDATED')
        return self.object.patient.get_absolute_url()
    

class TheatreBookingListView(DoctorRequiredMixin,ListView):
    model=TheatreBooking
    template_name='ehr/theatre/theatre_bookings.html'
    context_object_name='bookings'
    paginate_by = 10

    def get_queryset(self):
        theatrebooking = super().get_queryset().order_by('-updated')
        theatrebooking_filter = TheatreBookingFilter(self.request.GET, queryset=theatrebooking)
        return theatrebooking_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_bookings = self.get_queryset().count()
        context['total_bookings'] = total_bookings
        context['theatreBookingFilter'] = TheatreBookingFilter(self.request.GET, queryset=self.get_queryset())
        return context


class TheatreNotesCreateView(DoctorRequiredMixin,CreateView):
    model = TheatreNotes
    form_class = TheatreNotesForm
    template_name = 'ehr/theatre/theatre_notes.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context

    def get_success_url(self):
        messages.success(self.request, 'PATIENT THEATRE NOTES ADDED')
        return self.object.patient.get_absolute_url()


class TheatreNotesListView(DoctorRequiredMixin,ListView):
    model=TheatreNotes
    template_name='ehr/theatre/operated_list.html'
    context_object_name='operated'
    paginate_by = 10

    def get_queryset(self):
        theatre = super().get_queryset().order_by('-updated')
        theatre_filter = TheatreNotesFilter(self.request.GET, queryset=theatre)
        return theatre_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_operations = self.get_queryset().count()
        context['total_operations'] = total_operations
        context['theatreFilter'] = TheatreNotesFilter(self.request.GET, queryset=self.get_queryset())
        return context

    
    
class RadiologyTestCreateView(LoginRequiredMixin, CreateView):
    model = RadiologyResult
    form_class = RadiologyTestForm
    template_name = 'ehr/radiology/radiology_result.html'
        
    def form_valid(self, form):
        patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient
        form.instance.user = self.request.user

        radiology_result = form.save(commit=False)
        payment = Paypoint.objects.create(
            patient=patient,
            status=False,
            service=radiology_result.test, 
            price=radiology_result.test.price,
        )
        radiology_result.payment = payment 
        radiology_result.save()
        messages.success(self.request, 'Radiology test created successfully')
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.patient.get_absolute_url()


class RadiologyListView(ListView):
    model=RadiologyResult
    template_name='ehr/radiology/radiology_list.html'
    context_object_name='radiology_results'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(payment__status__isnull=False,payment__status=True).order_by('-updated')
        return queryset
    

class RadiologyResultCreateView(LoginRequiredMixin, UpdateView):
    model = RadiologyResult
    form_class = RadiologyResultForm
    template_name = 'ehr/radiology/radiology_result.html'
    success_url=reverse_lazy('radiology_request')

    def get_object(self, queryset=None):
        patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        return get_object_or_404(RadiologyResult, patient=patient, pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        radiology_result = form.save(commit=False)
        radiology_result.comments = form.cleaned_data['comments']
        radiology_result.save()
        messages.success(self.request, 'Radiology result updated successfully')
        return super().form_valid(form)


class RadiologyRequestListView(ListView):
    model=RadiologyResult
    template_name='ehr/radiology/radiology_request.html'
    context_object_name='radiology_request'
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(cleared=False)
        return queryset


@method_decorator(login_required(login_url='login'), name='dispatch')
class RadioReportView(ListView):
    model = RadiologyResult
    template_name = 'ehr/radiology/radiology_report.html'
    paginate_by = 10
    context_object_name = 'patient'

    def get_queryset(self):
        queryset = super().get_queryset()

        radio_filter = RadioFilter(self.request.GET, queryset=queryset)
        patient = radio_filter.qs.order_by('-updated')
        return patient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['radio_filter'] = RadioFilter(self.request.GET, queryset=self.get_queryset())
        return context
    

class BillingCreateView(DoctorRequiredMixin,LoginRequiredMixin,  FormView):
    template_name = 'ehr/revenue/billing.html'
    
    def get_form(self):
        BillingFormSet = modelformset_factory(Billing, form=BillingForm, extra=26)
        if self.request.method == 'POST':
            return BillingFormSet(self.request.POST)
        else:
            return BillingFormSet(queryset=Billing.objects.none())
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_form()
        context['patient'] = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        return context

    def form_valid(self, form):
        formset = self.get_form()
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.form_invalid(form)

    @transaction.atomic
    def formset_valid(self, formset):
        patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        bill = Bill.objects.create(user=self.request.user, patient=patient)
        
        total_amount = 0
        instances = formset.save(commit=False)
        
        for instance in instances:
            if instance.total_item_price:  # Only process non-empty forms
                instance.bill = bill
                total_amount += instance.total_item_price
                instance.save()
        
        # Update the bill with the total amount
        bill.total_amount = total_amount
        bill.save()

        # Create a single paypoint for the entire bill
        paypoint = Paypoint.objects.create(
            user=self.request.user,
            patient=patient,
            service=f"Surgery Bill-{bill.id}",
            price=total_amount,
            status=False
        )

        # Update all billing instances with the same paypoint
        Billing.objects.filter(bill=bill).update(payment=paypoint)

        return super().form_valid(formset)


    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        messages.success(self.request, 'BILL ADDED')
        return reverse('patient_details', kwargs={'file_no': self.kwargs['file_no']})


def get_category(request, category_id):
    items = TheatreItem.objects.filter(category_id=category_id)
    item_list = [{'id': item.id, 'name': item.name, 'price': float(item.price)} for item in items]
    return JsonResponse({'items': item_list})


class BillDetailView(DetailView):
    model = Bill
    template_name = 'ehr/revenue/bill_detail.html'
    context_object_name = 'bill'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add billing items to the context
        context['billing_items'] = Billing.objects.filter(bill=self.object).select_related('item', 'item__category')
        return context

    def get_queryset(self):
        return super().get_queryset().prefetch_related('items__item__category')



class BillingPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/bill_pay_list.html'
    context_object_name = 'bill_pays'
    paginate_by = 10

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        return Paypoint.objects.filter(service__startswith='Surgery Bill-').order_by('-updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        pay_total = queryset.count()
        total_worth = queryset.filter(status=True).aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        return context


class BillListView(DoctorRequiredMixin, LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'ehr/revenue/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 10

    def get_queryset(self):
        return Bill.objects.filter(user=self.request.user).prefetch_related('items').order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_bills'] = self.get_queryset().count()
        return context
    

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class BillPDFView(DetailView):
    model = Bill
    template_name = 'ehr/revenue/bill_pdf.html'

    def get(self, request, *args, **kwargs):
        bill = self.get_object()
        billing_items = Billing.objects.filter(bill=bill).select_related('item', 'item__category')
        
        context = {
            'bill': bill,
            'billing_items': billing_items,
        }
        
        pdf = render_to_pdf('ehr/revenue/bill_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            if 'download' in request.GET:
                filename = f"Bill_{bill.id}.pdf"
                content = f"attachment; filename={filename}"
                response['Content-Disposition'] = content
            return response
        return HttpResponse("Error generating PDF", status=400)