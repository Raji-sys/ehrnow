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
from django.db.models import Q
import os
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Prefetch
from django.db import transaction
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _

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

class DoctorNurseRecordRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='doctor').exists() or self.request.user.groups.filter(name='nurse').exists() or self.request.user.groups.filter(name='record')


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
        path = os.path.join(settings.STATIC_ROOT,uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.MEDIA_ROOT,uri.replace(settings.MEDIA_URL, ""))
    return path


@method_decorator(log_anonymous_required, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('get_started')
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
    template_name='get_started.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = [
        {'url': 'medical_record', 'text_color': 'text-slate-600', 'hover_bg_color': 'emerald-600', 'icon': 'fa-file-archive', 'name': 'MEDICAL RECORD'},
        {'url': 'revenue', 'text_color': 'text-emerald-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-cash-register', 'name': 'REVENUE'},
        {'url': 'nursing_desks_list', 'text_color': 'text-blue-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-stethoscope', 'name': 'NURSING'},
        {'url': 'clinic_list', 'text_color': 'text-gray-800',  'hover_bg_color': 'emerald-600', 'icon': 'fa-user-doctor', 'name': 'CLINIC'},
        {'url': 'pharmacy', 'text_color': 'text-indigo-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-prescription', 'name': 'PHARMACY'},
        {'url': 'pathology:dashboard', 'text_color': 'text-fuchsia-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-microscope', 'name': 'PATHOLOGY'},
        {'url': 'radiology', 'text_color': 'text-amber-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-x-ray', 'name': 'RADIOLOGY'},
        {'url': 'ward_list', 'text_color': 'text-purple-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-bed-pulse', 'name': 'WARD'},
        {'url': 'theatre', 'text_color': 'text-pink-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-head-side-mask', 'name': 'THEATRE'},
        {'url': 'physio', 'text_color': 'text-gray-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-wheelchair-move', 'name': 'PHYSIO'},
        {'url': 'store', 'text_color': 'text-rose-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-warehouse', 'name': 'STORE'},
        {'url': 'visit_report', 'text_color': 'text-emerald-600',  'hover_bg_color': 'emerald-600', 'icon': 'fa-chart-bar', 'name': 'CLINIC ACTIVITY REPORT'},
    ]
        return context
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class StaffDashboardView(TemplateView):
    template_name = "staff.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class MedicalRecordView(RecordRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/medical_record.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class PatientMovementView(TemplateView):
    template_name = "ehr/record/patient_moves.html"
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinics'] = Clinic.objects.all()
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class AppointmentDashboardView(TemplateView):
    template_name = "ehr/record/appt_dashboard.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class RevenueView(RevenueRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/revenue.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicDashView(DoctorNurseRecordRequiredMixin, ListView):
    model=Clinic
    context_object_name= 'clinics'
    template_name = "ehr/dashboard/clinic_list.html"
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class StoreView(TemplateView):
    template_name = "ehr/dashboard/store.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class ServiceView(TemplateView):
    template_name = "ehr/dashboard/service.html"

    
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
class TheatreListView(DoctorNurseRequiredMixin, ListView):
    model=Theatre
    context_object_name='theatres'
    template_name = "ehr/dashboard/theatre_list.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class TheatreDetailView(DoctorNurseRequiredMixin, DetailView):
    model=Theatre
    context_object_name='theatre'
    template_name = "ehr/theatre/theatre_detail.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class WardListView(DoctorNurseRequiredMixin, ListView):
    model = Ward
    context_object_name = 'wards'
    template_name = "ehr/dashboard/ward_list.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class WardDetailView(DoctorNurseRequiredMixin, DetailView):
    model = Ward
    template_name = "ehr/ward/ward_details.html"
    context_object_name = 'ward'
    paginate_by=10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admit_list_url'] = reverse('admission_list', kwargs={'ward_id': self.object.id, 'status': 'admit'})
        context['received_list_url'] = reverse('admission_list', kwargs={'ward_id': self.object.id, 'status': 'received'})
        context['discharged_list_url'] = reverse('admission_list', kwargs={'ward_id': self.object.id, 'status': 'discharge'})
        return context

class GenericWardListView(DoctorRequiredMixin, ListView):
    model = Admission  # Changed from Ward to Admission
    context_object_name = 'admissions'  # Changed from 'ward' to 'admissions'
    template_name = 'ehr/ward/generic_ward_list.html'
    paginate_by = 10  # Add pagination

    def get_queryset(self):
        ward = get_object_or_404(Ward, pk=self.kwargs['ward_id'])
        status = self.kwargs['status'].upper()
        queryset = Admission.objects.filter(ward=ward, status=status)

        # Add search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)
            )

        return queryset.order_by('-updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ward = get_object_or_404(Ward, pk=self.kwargs['ward_id'])
        context['ward'] = ward
        context['status'] = self.kwargs['status'].upper()
        context['admitted'] = Admission.objects.filter(ward=ward, status='ADMIT').count()
        context['received'] = Admission.objects.filter(ward=ward, status='RECEIVED').count()
        context['discharged'] = Admission.objects.filter(ward=ward, status='DISCHARGE').count()
        
        context['query'] = self.request.GET.get('q', '')        
        return context


class PatientCreateView(RecordRequiredMixin, CreateView):
    model = PatientData
    form_class = PatientForm
    template_name = 'ehr/record/new_patient.html'
    success_url = reverse_lazy("medical_record")

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient = form.save()
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
        queryset = super().get_queryset().order_by('-file_no')
        # Add search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(other_name__icontains=query) |
                Q(file_no__icontains=query)|
                Q(phone__icontains=query)|
                Q(title__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_count = self.get_queryset().count()
        total_patient=PatientData.objects.count()
        context['search_count'] = search_count
        context['total_patient'] = total_patient
        context['query'] = self.request.GET.get('q', '')

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


class VisitReportView(DoctorNurseRecordRequiredMixin, ListView):
    model = VisitRecord
    template_name = 'ehr/clinic/report.html'
    context_object_name = 'visits'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-updated')
        self.filterset = VisitFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.select_related('patient', 'clinic')  # Use select_related for efficiency

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visitFilter'] = self.filterset
        context['total_patient'] = PatientData.objects.count()
        context['filtered_count'] = self.filterset.qs.count()
        return context
    

@login_required
def visit_pdf(request):
    ndate = datetime.datetime.now()
    filename = ndate.strftime('on__%d/%m/%Y__at__%I.%M%p.pdf')
    f = VisitFilter(request.GET, queryset=VisitRecord.objects.all()).qs
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

    pisa_status = pisa.CreatePDF(get_template('ehr/clinic/visit_pdf.html').render(
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
        context = super().get_context_data(**kwargs)

        # Existing context data
        context['pc'] = PatientData.objects.all().count()
        context['gender_counts'] = PatientData.objects.values('gender').annotate(pc=Count('id'))
        context['geo_counts'] = PatientData.objects.values('zone').annotate(pc=Count('id'))
        context['state_counts'] = PatientData.objects.values('state').annotate(pc=Count('id'))
        context['lga_counts'] = PatientData.objects.values('lga').annotate(pc=Count('id'))
        context['religion_counts'] = PatientData.objects.values('religion').annotate(pc=Count('id'))
        context['marital_status_counts'] = PatientData.objects.values('marital_status').annotate(pc=Count('id'))
        context['nationality_counts'] = PatientData.objects.values('nationality').annotate(pc=Count('id'))
        context['occupation_counts'] = PatientData.objects.values('occupation').annotate(pc=Count('id'))
        context['role_in_occupation_counts'] = PatientData.objects.values('role_in_occupation').annotate(pc=Count('id'))
        context['address_counts'] = PatientData.objects.values('address').annotate(pc=Count('id'))

        # Data for charts
        gender_counts = list(context['gender_counts'])
        geo_counts = list(context['geo_counts'])
        state_counts = list(context['state_counts'])
        lga_counts = list(context['lga_counts'])
        religion_counts = list(context['religion_counts'])
        marital_status_counts = list(context['marital_status_counts'])
        nationality_counts = list(context['nationality_counts'])
        occupation_counts = list(context['occupation_counts'])
        role_in_occupation_counts = list(context['role_in_occupation_counts'])
        address_counts = list(context['address_counts'])

        context.update({
            'gender_labels': json.dumps([g['gender'] for g in gender_counts], cls=DjangoJSONEncoder),
            'gender_data': json.dumps([g['pc'] for g in gender_counts], cls=DjangoJSONEncoder),
            'geo_labels': json.dumps([gz['zone'] for gz in geo_counts], cls=DjangoJSONEncoder),
            'geo_data': json.dumps([gz['pc'] for gz in geo_counts], cls=DjangoJSONEncoder),
            'state_labels': json.dumps([s['state'] for s in state_counts], cls=DjangoJSONEncoder),
            'state_data': json.dumps([s['pc'] for s in state_counts], cls=DjangoJSONEncoder),
            'religion_labels': json.dumps([r['religion'] for r in religion_counts], cls=DjangoJSONEncoder),
            'religion_data': json.dumps([r['pc'] for r in religion_counts], cls=DjangoJSONEncoder),
            'marital_status_labels': json.dumps([m['marital_status'] for m in marital_status_counts], cls=DjangoJSONEncoder),
            'marital_status_data': json.dumps([m['pc'] for m in marital_status_counts], cls=DjangoJSONEncoder),
            'nationality_labels': json.dumps([n['nationality'] for n in nationality_counts], cls=DjangoJSONEncoder),
            'nationality_data': json.dumps([n['pc'] for n in nationality_counts], cls=DjangoJSONEncoder),
            'occupation_labels': json.dumps([o['occupation'] for o in occupation_counts], cls=DjangoJSONEncoder),
            'occupation_data': json.dumps([o['pc'] for o in occupation_counts], cls=DjangoJSONEncoder),
            'role_in_occupation_labels': json.dumps([r['role_in_occupation'] for r in role_in_occupation_counts], cls=DjangoJSONEncoder),
            'role_in_occupation_data': json.dumps([r['pc'] for r in role_in_occupation_counts], cls=DjangoJSONEncoder),
            'lga_labels': json.dumps([l['lga'] for l in lga_counts], cls=DjangoJSONEncoder),
            'lga_data': json.dumps([l['pc'] for l in lga_counts], cls=DjangoJSONEncoder),
            'address_labels': json.dumps([a['address'] for a in address_counts], cls=DjangoJSONEncoder),
            'address_data': json.dumps([a['pc'] for a in address_counts], cls=DjangoJSONEncoder),
        })
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
        context['visits'] = patient.visit_record.all().order_by('-updated')
        context['vitals'] = patient.vital_signs.all().order_by('-updated')
        context['payments'] = patient.patient_payments.all().order_by('-updated')
        context['clinical_notes'] = patient.clinical_notes.all().order_by('-updated')
        context['prescribed_drugs'] = patient.prescribed_drugs.all().order_by('-updated')
        context['hematology_results']=patient.hematology_result.all().order_by('-created')
        context['chempath_results']=patient.chemical_pathology_results.all().order_by('-created')
        context['micro_results']=patient.microbiology_results.all().order_by('-created')
        context['serology_results']=patient.serology_results.all().order_by('-created')
        context['radiology_results'] = patient.radiology_results.all().order_by('-updated')
        context['admission_info'] = patient.admission_info.all().order_by('-updated')
        context['ward_vital_signs'] = patient.ward_vital_signs.all().order_by('-updated')
        context['ward_medication'] = patient.ward_medication.all().order_by('-updated')
        context['ward_clinical_notes'] = patient.ward_clinical_notes.all().order_by('-updated')
        context['theatre_bookings'] = patient.theatre_bookings.all().order_by('-updated')
        context['operation_notes'] = patient.operation_notes.all().order_by('-updated')
        context['anaesthesia_checklist'] = patient.anaesthesia_checklist.all().order_by('-updated')
        context['theatre_operation_record'] = patient.theatre_operation_record.all().order_by('-updated')
        context['surgery_bill'] = patient.surgery_bill.all().order_by('-created')
        context['private_bill'] = patient.private_bill.all().order_by('-created')
        context['archive'] = patient.patient_archive.all().order_by('-updated')

         # Check if the patient has a wallet
        if hasattr(patient, 'wallet'):
            # Retrieve wallet transactions
            context['wallet'] = patient.wallet.transactions.all().order_by('-created_at')
        else:
            context['wallet'] = []

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
   

class VisitCreateView(LoginRequiredMixin, CreateView):
    model = VisitRecord
    form_class = VisitForm
    template_name = 'ehr/record/visit.html'
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['file_no'] = self.kwargs['file_no']
        return kwargs

    def form_valid(self, form):
        patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        
        # Check for existing open visit
        existing_open_visit = VisitRecord.objects.filter(
            patient=patient,
            seen=False
        ).exists()

        if existing_open_visit:
            form.add_error(None, ValidationError(
                _("This patient already has an open visit. Please close the existing visit before creating a new one."),
                code='duplicate_visit'
            ))
            return self.form_invalid(form)

        form.instance.patient = patient
        form.instance.user = self.request.user
        form.instance.clinic = form.cleaned_data['clinic']

        visit = form.save(commit=False)
        payment = Paypoint.objects.create(
            patient=patient,
            status=False,
            service=visit.record, 
            price=visit.record.price,
        )
        visit.payment = payment
        visit.vitals = False
        visit.save()

        if payment.status:
            nursing_desk = NursingDesk.objects.filter(clinic=patient.clinic).first()
            if nursing_desk:
                messages.success(self.request, f'Payment successful. Patient sent to {nursing_desk} for vital signs.')
            else:
                messages.warning(self.request, f'Payment successful, but no nursing desk available for {patient.clinic}.')
        else:
            messages.warning(self.request, 'Proceed to revenue station and complete the payment.')
        
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.patient.get_absolute_url()


class VisitPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/visit_pay_list.html'
    context_object_name = 'visit_pays'
    paginate_by = 10

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        return Paypoint.objects.filter(record_payment__isnull=False).order_by('-updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        return context  


class NursingStationDetailView(DetailView):
    model = NursingDesk
    template_name = 'ehr/nurse/nursing_station.html'
    context_object_name = 'nursing_desk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch patients whose payment is complete and who are assigned to the current nursing desk's clinic
        visits = VisitRecord.objects.filter(
            clinic=self.object.clinic,  # Match the clinic with the nursing desk
            payment__status=True,
            vitals=False
        ).select_related('patient', 'payment', 'record')

        # Pass the list of visit records to the template
        context['visits'] = visits
        return context


class NursingDeskListView(ListView):
    model = NursingDesk
    template_name = 'ehr/nurse/nursing_desk.html'
    context_object_name = 'nursing_desks'

    def get_queryset(self):
        queryset = super().get_queryset()
        for desk in queryset:
            # Count patients with completed payment waiting for vital signs
            desk.patient_count = VisitRecord.objects.filter(
                clinic=desk.clinic,
                payment__status=True,# Ensure the payment is complete
                vitals=False
            ).count()
        return queryset


class VitalSignCreateView(NurseRequiredMixin, CreateView):
    model = VitalSigns
    form_class = VitalSignsForm
    template_name = 'ehr/nurse/vital_signs.html'
    success_url = reverse_lazy('nursing_desks_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        visit_record = VisitRecord.objects.filter(patient__file_no=self.kwargs['file_no']).latest('id')
        kwargs['clinic'] = visit_record.clinic
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        visit_record = VisitRecord.objects.filter(patient__file_no=self.kwargs['file_no']).latest('id')
        form.instance.patient = visit_record.patient
        form.instance.clinic = visit_record.clinic
        room = form.cleaned_data.get('room')

        self.object = form.save()

        visit_record.vitals = True
        visit_record.room = room
        visit_record.save()

        messages.success(self.request, 'Vital signs recorded. Patient has been moved to consultation.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visit_record'] = VisitRecord.objects.filter(patient__file_no=self.kwargs['file_no']).latest('id')
        return context
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicDetailView(DoctorNurseRecordRequiredMixin, DetailView):
    model = Clinic
    context_object_name = 'clinic'
    template_name = "ehr/clinic/clinic_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms = self.object.consultation_rooms.all()
        context['rooms'] = rooms        
        for room in rooms:
            room.waiting_count = VisitRecord.objects.filter(
                clinic=self.object,
                room=room,
                vitals=True,
                seen=False
            ).count()

        context['waiting_count'] = VisitRecord.objects.filter(
            clinic=self.object,
            vitals=True,
            seen=False
        ).count()
        context['seen_count'] = VisitRecord.objects.filter(
            clinic=self.object,
            seen=True,
        ).count()
        context['review_count'] = VisitRecord.objects.filter(
            clinic=self.object,
            review=True
        ).count()
        return context
    
    
class VisitListView(DoctorNurseRecordRequiredMixin, ListView):
    model = VisitRecord
    template_name = 'ehr/clinic/pt_list.html'  # Base template
    context_object_name = 'visits'
    filter_params = {}

    def get_queryset(self):
        self.clinic = get_object_or_404(Clinic, pk=self.kwargs['clinic_id'])
        queryset = VisitRecord.objects.filter(
            clinic=self.clinic,
            updated__gte=timezone.now() - timedelta(days=100),
            **self.filter_params
        ).order_by('-updated')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic'] = self.clinic
        return context

class WaitingListView(VisitListView):
    filter_params = {
        'vitals': True,
        'seen': False
    }
    template_name = 'ehr/clinic/waiting_list.html'  # Custom template if needed

class SeenListView(VisitListView):
    filter_params = {
        'seen': True
    }
    template_name = 'ehr/clinic/seen_list.html'

class ReviewListView(VisitListView):
    filter_params = {
        'review': True
    }
    template_name = 'ehr/clinic/review_list.html'


@method_decorator(login_required(login_url='login'), name='dispatch')
class RoomDetailView(DoctorNurseRequiredMixin, DetailView):
    model = Room
    template_name = 'ehr/clinic/room_details.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = VisitRecord.objects.filter(
        room=self.object,
        seen=False 
    ).select_related('patient').order_by('-updated')
        return context
        

@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicalNoteCreateView(DoctorRequiredMixin, CreateView):
    model = ClinicalNote
    form_class = ClinicalNoteForm
    template_name = 'ehr/doctor/clinical_note.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient_data = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()
        
        visit = VisitRecord.objects.filter(patient__file_no=self.kwargs['file_no']).order_by('-id').first()        
        if form.instance.needs_review:
            visit.review = True
            visit.save()
            messages.success(self.request, 'Clinical note created. Patient awaiting review.')
        else:
            visit.close_visit()
            messages.success(self.request, 'Clinical note created. Patient consultation completed.')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        return context

    def get_success_url(self):
        return self.object.patient.get_absolute_url()



@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicalNoteUpdateView(DoctorRequiredMixin, UpdateView):
    model = ClinicalNote
    template_name = 'ehr/doctor/update_clinical_note.html'
    form_class = ClinicalNoteUpdateForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Clinical note updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.patient.get_absolute_url()


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
        queryset = super().get_queryset().order_by('-updated')
        # Add search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(other_name__icontains=query) |
                Q(file_no__icontains=query)|
                Q(phone__icontains=query)|
                Q(title__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')

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
        paypoint = form.save(commit=False)
        messages.success(self.request, 'TRANSACTION SUCCESSFULLY')
        return super().form_valid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        # Add wallet balance to context

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()


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

    @transaction.atomic
    def form_valid(self, form):
        form.instance.user = self.request.user
        paypoint = form.save(commit=False)
        try:
            paypoint.save()

            if paypoint.service.startswith("Surgery Bill:"):
                wallet, created = Wallet.objects.get_or_create(patient=paypoint.patient)
                wallet.add_funds(paypoint.price)

            messages.success(self.request, 'TRANSACTION SUCCESSFUL')
            return super().form_valid(form)
        except ValidationError as e:
            error_message = str(e)
            if "Insufficient funds" in error_message:
                error_message = "Insufficient funds in the wallet. Please add funds and try again."
            form.add_error(None, error_message)
            return self.form_invalid(form)


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
    paginate_by = 3

    def get_queryset(self):
        # We'll handle this in get_context_data
        return Paypoint.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        hematology_pays = Paypoint.objects.filter(hematology_result_payment__isnull=False).order_by('-updated')
        chempath_pays = Paypoint.objects.filter(chempath_result_payment__isnull=False).order_by('-updated')
        micro_pays = Paypoint.objects.filter(micro_result_payment__isnull=False).order_by('-updated')
        serology_pays = Paypoint.objects.filter(serology_result_payment__isnull=False).order_by('-updated')

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

        # Combined total worth
        combined_total_worth = hema_total_worth + chem_total_worth + micro_total_worth + serology_total_worth

        context['hematology_pays'] = hematology_pays
        context['chempath_pays'] = chempath_pays
        context['micro_pays'] = micro_pays
        context['serology_pays'] = serology_pays

        context['hema_pay_total'] = hema_pay_total
        context['chem_pay_total'] = chem_pay_total
        context['micro_pay_total'] = micro_pay_total
        context['serology_pay_total'] = serology_pay_total

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

    def get_success_url(self):
        ward_id = self.object.ward.id
        status = self.object.status
        return reverse('admission_list', kwargs={'ward_id': ward_id, 'status': status})

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.is_valid():
            form.save()
            messages.success(self.request, 'PATIENT UPDATED')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.get_success_url()
        return context


class AdmissionDischargeView(UpdateView):
    model = Admission
    template_name = 'ehr/ward/update_admission.html'
    form_class = AdmissionDischargeForm

    def get_success_url(self):
        ward_id = self.object.ward.id
        status = self.object.status
        return reverse('admission_list', kwargs={'ward_id': ward_id, 'status': status})

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.is_valid():
            form.save()
            messages.success(self.request, 'PATIENT UPDATED')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.get_success_url()
        return context


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
            service=f"Surgery Bill:-{bill.id}",
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
        return Paypoint.objects.filter(service__startswith='Surgery Bill:-').order_by('-updated')

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
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)
        theatrebooking = super().get_queryset().filter(theatre=theatre).order_by('-updated')
        theatrebooking_filter = TheatreBookingFilter(self.request.GET, queryset=theatrebooking)
        return theatrebooking_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)

        total_bookings = self.get_queryset().count()
        
        context['theatre'] = theatre
        context['total_bookings'] = total_bookings
        context['theatreBookingFilter'] = TheatreBookingFilter(self.request.GET, queryset=self.get_queryset())
        return context


class OperationNotesCreateView(DoctorRequiredMixin,CreateView):
    model = OperationNotes
    form_class = OperationNotesForm
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


class OperationNotesListView(DoctorRequiredMixin,ListView):
    model=OperationNotes
    template_name='ehr/theatre/operated_list.html'
    context_object_name='operated'
    paginate_by = 10

    def get_queryset(self):
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)
        operated = super().get_queryset().filter(theatre=theatre).order_by('-updated')
        theatre_filter = OperationNotesFilter(self.request.GET, queryset=operated)
        return theatre_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)

        total_operations = self.get_queryset().count()
        context['theatre'] = theatre
        context['total_operations'] = total_operations
        context['theatreFilter'] = OperationNotesFilter(self.request.GET, queryset=self.get_queryset())
        return context


class AnaesthesiaChecklistCreateView(DoctorRequiredMixin,CreateView):
    model = AnaesthisiaChecklist
    form_class = AnaesthisiaChecklistForm
    template_name = 'ehr/theatre/anaesthesia_checklist.html'

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context

    def get_success_url(self):
        messages.success(self.request, 'ANAESTHESIA CHECKLIST ADDED')
        return self.object.patient.get_absolute_url()


class AnaesthesiaChecklistListView(DoctorRequiredMixin,ListView):
    model=AnaesthisiaChecklist
    template_name='ehr/theatre/anaesthesia_checklist_list.html'
    context_object_name='anaesthesia_checklist'
    paginate_by = 10

    def get_queryset(self):
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)
        anaesthesia_checklist = super().get_queryset().filter(theatre=theatre).order_by('-updated')
        anaesthesia_checklist_filter = AnaesthisiaChecklistFilter(self.request.GET, queryset=anaesthesia_checklist)
        return anaesthesia_checklist_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)
        
        total_operations = self.get_queryset().count()
        context['theatre'] = theatre
        context['total_operations'] = total_operations

        context['anaesthesia_checklistFilter'] = AnaesthisiaChecklistFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PrivateBillingCreateView(DoctorRequiredMixin,LoginRequiredMixin,  FormView):
    template_name = 'ehr/revenue/private_billing.html'
    
    def get_form(self):
        PrivateBillingFormSet = modelformset_factory(PrivateBilling, form=PrivateBillingForm, extra=17)
        if self.request.method == 'POST':
            return PrivateBillingFormSet(self.request.POST)
        else:
            return PrivateBillingFormSet(queryset=PrivateBilling.objects.none())
        
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
        private_bill = PrivateBill.objects.create(user=self.request.user, patient=patient)
        
        total_amount = 0
        instances = formset.save(commit=False)
        
        for instance in instances:
            if instance.price:  # Only process non-empty forms
                instance.private_bill = private_bill
                total_amount += instance.price
                instance.save()
        
        # Update the bill with the total amount
        private_bill.total_amount = total_amount
        private_bill.save()

        # Create a single paypoint for the entire bill
        paypoint = Paypoint.objects.create(
            user=self.request.user,
            patient=patient,
            service=f"Surgery Bill-{private_bill.id}",
            price=total_amount,
            status=False
        )
        # Update all billing instances with the same paypoint
        PrivateBilling.objects.filter(private_bill=private_bill).update(payment=paypoint)

        return super().form_valid(formset)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        messages.success(self.request, 'BILL ADDED')
        return reverse('patient_details', kwargs={'file_no': self.kwargs['file_no']})


class PrivateBillDetailView(DetailView):
    model = PrivateBill
    template_name = 'ehr/revenue/private_bill_detail.html'
    context_object_name = 'private_bill'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['private_billing_items'] = PrivateBilling.objects.filter(private_bill=self.object).select_related('item')
        
        # Get the latest TheatreBooking for the patient
        theatre_booking = TheatreBooking.objects.filter(patient=self.object.patient).order_by('-date').first()
        context['theatre_booking'] = theatre_booking
        
        return context
        

class PrivateBillingPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/private_bill_pay_list.html'
    context_object_name = 'private_bill_pays'
    paginate_by = 10

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        return Paypoint.objects.filter(service__startswith='Private Surgery Bill:-').order_by('-updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        pay_total = queryset.count()
        total_worth = queryset.filter(status=True).aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        return context


class PrivateBillListView(DoctorRequiredMixin, LoginRequiredMixin, ListView):
    model = PrivateBill
    template_name = 'ehr/revenue/private_bill_list.html'
    context_object_name = 'private_bills'
    paginate_by = 10

    def get_queryset(self):
        return PrivateBill.objects.filter(user=self.request.user).prefetch_related('items').order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_bills'] = self.get_queryset().count()
        return context
    

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result, link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class PrivateBillPDFView(DetailView):
    model = PrivateBill
    template_name = 'ehr/revenue/private_bill_pdf.html'

    def get(self, request, *args, **kwargs):
        private_bill = self.get_object()
        private_billing_items = PrivateBilling.objects.filter(private_bill=private_bill).select_related('item')
        theatre_booking = TheatreBooking.objects.filter(patient=private_bill.patient).order_by('-date').first()
        
        # Get the full path to the logo
        logo_path = staticfiles_storage.path('images/logo.jpg')
        
        context = {
            'private_bill': private_bill,
            'private_billing_items': private_billing_items,
            'theatre_booking': theatre_booking,
            'logo_path': logo_path,
        }
        
        pdf = render_to_pdf('ehr/revenue/private_bill_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            if 'download' in request.GET:
                filename = f"Bill_{private_bill.id}.pdf"
                content = f"attachment; filename={filename}"
                response['Content-Disposition'] = content
            return response
        return HttpResponse("Error generating PDF", status=400) 


class FundWalletView(CreateView):
    model = WalletTransaction
    fields = ['amount']
    template_name = 'ehr/revenue/fund_wallet.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(pk=self.kwargs['patient_pk'])
        return context
    
    def get_success_url(self):
        return reverse_lazy('patient_details', kwargs={'file_no': self.object.wallet.patient.file_no})

    def form_valid(self, form):
        patient = PatientData.objects.get(pk=self.kwargs['patient_pk'])
        form.instance.wallet = patient.wallet
        form.instance.transaction_type = 'CREDIT'
        form.instance.description = 'Wallet funding'
        messages.success(self.request, f'Successfully added {form.instance.amount} to wallet')
        return super().form_valid(form)


class AllTransactionsListView(LoginRequiredMixin, ListView):
    model = WalletTransaction
    template_name = 'ehr/revenue/wallet_transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10 

    def get_queryset(self):
        return WalletTransaction.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_credit'] = WalletTransaction.objects.filter(transaction_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_debit'] = WalletTransaction.objects.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or 0
        context['net_balance'] = context['total_credit'] - context['total_debit']
        return context
    

class TheatreOperationRecordCreateView(CreateView):
    model = TheatreOperationRecord
    form_class = TheatreOperationRecordForm
    template_name = 'ehr/theatre/theatre_record.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['consumables'] = ConsumableUsageFormSet(self.request.POST)
            data['implants'] = ImplantUsageFormSet(self.request.POST)
        else:
            data['consumables'] = ConsumableUsageFormSet()
            data['implants'] = ImplantUsageFormSet()
        return data

    def form_valid(self, form):
        form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        context = self.get_context_data()
        consumables = context['consumables']
        implants = context['implants']
        with transaction.atomic():
            self.object = form.save()
            if consumables.is_valid():
                consumables.instance = self.object
                consumables.save()
            if implants.is_valid():
                implants.instance = self.object
                implants.save()
        self.object=form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'SURGERY RECORD ADDED')
        return self.object.patient.get_absolute_url()


class TheatreOperationRecordListView(DoctorRequiredMixin, ListView):
    model = TheatreOperationRecord
    template_name = 'ehr/theatre/theatre_record_list.html'
    context_object_name = 'surgical_records'
    paginate_by = 10

    def get_queryset(self):
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)
        
        queryset = super().get_queryset().filter(theatre=theatre).order_by('-updated')
        theatre_op_filter = TheatreOperationRecordFilter(self.request.GET, queryset=queryset)
        
        return theatre_op_filter.qs.prefetch_related(
            Prefetch('consumableusage_set', queryset=ConsumableUsage.objects.select_related('consumable')),
            Prefetch('implantusage_set', queryset=ImplantUsage.objects.select_related('implant'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)
        
        context['theatre'] = theatre
        context['total_operations'] = self.get_queryset().count()
        context['theatreOpFilter'] = TheatreOperationRecordFilter(self.request.GET, queryset=self.get_queryset())
        
        return context


class ArchiveCreateView(CreateView):
    model=Archive
    template_name='ehr/archive_form.html'
    form_class=ArchiveForm

    def form_valid(self, form):
        form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        self.object = form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'RECORD ADDED')
        return self.object.patient.get_absolute_url()


class ArchiveUpdateView(UpdateView):
    model=Archive
    template_name='ehr/archive_form.html'
    form_class=ArchiveForm
    
    def get_success_url(self):
        messages.success(self.request, 'RECORD UPDATED ADDED')
        return self.object.patient.get_absolute_url()


class ArchiveDeleteView(DeleteView):
    model = Archive
    template_name = 'ehr/confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, 'File deleted successfully.')
        return self.object.patient.get_absolute_url()