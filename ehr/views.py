from django.shortcuts import get_object_or_404, redirect, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views import View
from django.utils.decorators import method_decorator
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
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, FormView
from django.utils import timezone
from datetime import timedelta
User = get_user_model()
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
from django.http import JsonResponse, request
from django.db import transaction
from django.db.models import Sum, Count, Q
from datetime import datetime
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Prefetch
from django.db import transaction
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _
from django.template.loader import get_template
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect
from results.models import GenericTest 
from django.db.models import OuterRef, Subquery
from django.core.paginator import Paginator
from django.db.models import Subquery, OuterRef

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
        return reverse_lazy('stafflist')


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
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-user_id')
        # Add search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query)|
                Q(phone__icontains=query)|
                Q(unit__name__icontains=query)|
                Q(department__name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_profiles = self.get_queryset().count()
        search_count = self.get_queryset().count()
        context['search_count'] = search_count
        context['total_profiles'] = total_profiles
        context['query'] = self.request.GET.get('q', '')

        return context
    
class IndexView(TemplateView):
    template_name = "index.html"
    # template_name = "get_started.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class GetStartedView(TemplateView):
    template_name='get_started.html'
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class StaffDashboardView(TemplateView):
    template_name = "staff.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class MedicalRecordView(RecordRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/medical_record.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class AppointmentDashboardView(TemplateView):
    template_name = "ehr/record/appt_dashboard.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class RevenueView(RevenueRequiredMixin,TemplateView):
    template_name = "ehr/dashboard/revenue.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class BillingHomeView(RevenueRequiredMixin,TemplateView):
    template_name = "ehr/revenue/billing_home.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicDashView(DoctorNurseRecordRequiredMixin, ListView):
    model=Clinic
    context_object_name= 'clinics'
    template_name = "ehr/dashboard/clinic_list.html"
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class StoreView(TemplateView):
    template_name = "ehr/dashboard/store.html"

    
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

class GenericWardListView(DoctorNurseRequiredMixin, ListView):
    model = Admission  # Changed from Ward to Admission
    context_object_name = 'admissions'  # Changed from 'ward' to 'admissions'
    template_name = 'ehr/ward/generic_ward_list.html'
    paginate_by = 20  # Add pagination

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
                Q(patient__file_no__icontains=query)|
                Q(patient__title__icontains=query)|
                Q(patient__phone__icontains=query)
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
        messages.success(self.request, 'Patient Information Updated Successfully')
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, 'Error updating patient information')
        return self.render_to_response(self.get_context_data(form=form))


class PatientListView(ListView):
    model=PatientData
    template_name='ehr/record/patient_list.html'
    context_object_name='patients'
    paginate_by = 20

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
                Q(title__icontains=query)|
                Q(gender__iexact=query)
    
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_count = self.get_queryset().count()
        total_patient=PatientData.objects.count()
        context['is_revenue'] = self.request.user.groups.filter(name='revenue').exists()
        context['search_count'] = search_count
        context['total_patient'] = total_patient
        context['query'] = self.request.GET.get('q', '')

        return context


class PatientWalletListView(ListView):
    model=PatientData
    template_name='ehr/revenue/patient_wallet_list.html'
    context_object_name='patients'
    paginate_by = 20

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
                Q(title__icontains=query)|
                Q(gender__iexact=query)
    
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_count = self.get_queryset().count()
        total_patient=PatientData.objects.count()
        context['is_revenue'] = self.request.user.groups.filter(name='revenue').exists()
        context['search_count'] = search_count
        context['total_patient'] = total_patient
        context['query'] = self.request.GET.get('q', '')

        return context


class PatientReportView(ListView):
    model = PatientData
    template_name = 'ehr/report/patient_report.html'
    context_object_name = 'patients'
    paginate_by = 20

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
    ndate = datetime.now()
    filename = ndate.strftime('on__%d/%m/%Y__at__%I.%M%p.pdf')
    f = PatientReportFilter(request.GET, queryset=PatientData.objects.all()).qs
    values = []
    for key, value in request.GET.items():
        if value:
            values.append(f"{key.capitalize().replace('_', ' ')}: {value}")
    
    result = ", ".join(values)

    context = {'generated_date': datetime.now().strftime('%d-%h-%Y'),
            'user': request.user.username.upper(),'f': f, 'pagesize': 'A4',
            'orientation': 'landscape', 'result': result,}

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


# class VisitReportView(ListView):
#     model = VisitRecord
#     filterset_class = VisitFilter
#     template_name = 'ehr/clinic/report.html'
#     context_object_name = 'visits'
#     paginate_by = 20

#     def get_queryset(self):
#         # Subquery to get the latest ClinicalNote for each patient
#         latest_note = ClinicalNote.objects.filter(patient=OuterRef('patient')).order_by('-updated').values('diagnosis')[:1]

#         # Annotate the VisitRecord queryset with the latest clinical note's diagnosis
#         self.filterset = VisitFilter(
#             self.request.GET, 
#             queryset=VisitRecord.objects.select_related('patient', 'clinic', 'team')
#             .annotate(latest_diagnosis=Subquery(latest_note))
#         )
#         return self.filterset.qs.order_by('-updated')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Add total patient count and filtered count to the context
#         context['total_patient'] = PatientData.objects.count()
#         context['filtered_count'] = self.filterset.qs.count()
#         context['visitFilter'] = self.filterset

#         return context
class VisitReportView(ListView):
    model = VisitRecord
    filterset_class = VisitFilter
    template_name = 'ehr/clinic/report.html'
    context_object_name = 'visits'
    paginate_by = 20
    
    def get_queryset(self):
        # Default time filter if none specified (100 days)
        days_filter = 100
        time_threshold = timezone.now() - timedelta(days=days_filter)
        
        # Base queryset with time filter
        queryset = VisitRecord.objects.select_related('patient', 'clinic', 'team')
        
        # Apply date filter if not explicitly provided in request
        if not (self.request.GET.get('date_from') or self.request.GET.get('date_to')):
            queryset = queryset.filter(updated__gte=time_threshold)
            
        # Get latest clinical note for diagnosis
        latest_note = ClinicalNote.objects.filter(
            patient=OuterRef('patient')
        ).order_by('-updated').values('diagnosis')[:1]
        
        # Annotate with diagnosis
        queryset = queryset.annotate(latest_diagnosis=Subquery(latest_note))
        
        # Apply filters
        self.filterset = VisitFilter(self.request.GET, queryset=queryset)
        
        return self.filterset.qs.order_by('-updated')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add total patient count and filtered count
        context['total_patient'] = PatientData.objects.count()
        context['filtered_count'] = self.filterset.qs.count()
        context['visitFilter'] = self.filterset
        
        # Get counts for each status
        context['awaiting_nurse_count'] = self.filterset.qs.filter(vitals=False).count()
        context['awaiting_doctor_count'] = self.filterset.qs.filter(
            vitals=True, seen=False, review=False
        ).count()
        context['seen_count'] = self.filterset.qs.filter(seen=True, review=False).count()
        context['awaiting_review_count'] = self.filterset.qs.filter(review=True).count()
        
        return context


class VisitStatCardView(TemplateView):
    template_name = 'ehr/clinic/report_stat_card.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date and time periods
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Basic stats
        context['total_patient'] = PatientData.objects.count()
        
        # Time period stats for all visits
        visits_all_time = VisitRecord.objects.filter(seen=True)
        context['total_patients_seen'] = visits_all_time.count()
        context['patients_seen_today'] = visits_all_time.filter(updated__gte=today_start).count()
        context['patients_seen_this_week'] = visits_all_time.filter(updated__gte=week_start).count()
        context['patients_seen_this_month'] = visits_all_time.filter(updated__gte=month_start).count()
        context['patients_seen_this_year'] = visits_all_time.filter(updated__gte=year_start).count()
        
        # Recent visits stats (100 days)
        days_filter = 100
        time_threshold = timezone.now() - timedelta(days=days_filter)
        visits = VisitRecord.objects.filter(updated__gte=time_threshold)
        context['filtered_count'] = visits.count()
        
        # Gender breakdown
        male_patients = visits_all_time.filter(patient__gender='MALE').count()
        female_patients = visits_all_time.filter(patient__gender='FEMALE').count()
        
        context['male_patients_seen'] = male_patients
        context['female_patients_seen'] = female_patients
        
        # Per clinic stats
        clinics = Clinic.objects.all()
        context['clinic_count'] = clinics.count()
        
        clinic_stats = []
        for clinic in clinics:
            clinic_stats.append({
                'name': clinic.name,
                'total_seen': visits_all_time.filter(clinic=clinic).count(),
                'seen_today': visits_all_time.filter(clinic=clinic, updated__gte=today_start).count(),
                'seen_this_week': visits_all_time.filter(clinic=clinic, updated__gte=week_start).count(),
                'seen_this_month': visits_all_time.filter(clinic=clinic, updated__gte=month_start).count(),
                'seen_this_year': visits_all_time.filter(clinic=clinic, updated__gte=year_start).count()
            })
        context['clinic_stats'] = clinic_stats
        
        # Per team stats
        teams = Team.objects.all()
        context['team_count'] = teams.count()
        
        team_stats = []
        for team in teams:
            team_stats.append({
                'name': team.name,
                'total_seen': visits_all_time.filter(team=team).count(),
                'seen_today': visits_all_time.filter(team=team, updated__gte=today_start).count(),
                'seen_this_week': visits_all_time.filter(team=team, updated__gte=week_start).count(),
                'seen_this_month': visits_all_time.filter(team=team, updated__gte=month_start).count(),
                'seen_this_year': visits_all_time.filter(team=team, updated__gte=year_start).count()
            })
        context['team_stats'] = team_stats
        
        # Get counts for each status
        context['awaiting_nurse_count'] = visits.filter(vitals=False).count()
        context['awaiting_doctor_count'] = visits.filter(
            vitals=True, seen=False, review=False
        ).count()
        context['seen_count'] = visits.filter(seen=True, review=False).count()
        context['awaiting_review_count'] = visits.filter(review=True).count()
        
        return context

@login_required
def visit_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on__%d/%m/%Y__at__%I.%M%p.pdf')

    # Subquery to get the latest clinical note for each patient
    latest_note_subquery = ClinicalNote.objects.filter(
        patient=OuterRef('patient')
    ).order_by('-updated').values('diagnosis')[:1]

    # Annotating the VisitRecord queryset with the latest diagnosis
    f = VisitFilter(request.GET, queryset=VisitRecord.objects.annotate(
        latest_diagnosis=Subquery(latest_note_subquery)
    )).qs
    
    patient = f.first().patient if f.exists() else None
    values = []
    for key, value in request.GET.items():
        if value:
            if key == 'clinic':
                clinic = Clinic.objects.get(id=value)
                values.append(f"Clinic: {clinic.name}")
            elif key == 'team':
                team = Team.objects.get(id=value)
                values.append(f"Team: {team.name}")
            else:
                values.append(f"{key.capitalize()}: {value}")
    
    result = ", ".join(values)

    context = {'generated_date': datetime.now().strftime('%d-%h-%Y'),
            'user': request.user.username.upper(),'f': f, 'pagesize': 'A4',
            'orientation': 'landscape', 'result': result,'patient': patient,}

    response = HttpResponse(content_type='application/pdf',
                            headers={'Content-Disposition': f'filename="Report__{filename}"'})

    buffer = BytesIO()

    # Render the PDF with the updated context
    pisa_status = pisa.CreatePDF(
        get_template('ehr/clinic/visit_pdf.html').render(context),
        dest=buffer,
        encoding='utf-8',
        link_callback=fetch_resources
    )

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
        context['test_items'] = (patient.test_items.all().prefetch_related('items__payment').order_by('-updated'))
        context['radiology_test_items'] = (patient.radiology_test_items.all().prefetch_related('payment').order_by('-updated'))
    # If 'created' field is reliably auto_now_add=True, order_by('-created', '-id') is more robust.
        all_visits_qs = patient.visit_record.all().order_by('-created','-id')
        context['visits'] = all_visits_qs

        latest_overall_visit = all_visits_qs.first()
        context['latest_overall_visit'] = latest_overall_visit # For display purposes

        has_active_visit_flag = False
        active_visit_for_actions = None

        if latest_overall_visit and latest_overall_visit.consultation:
            # The most recent visit is an active consultation
            has_active_visit_flag = True
            active_visit_for_actions = latest_overall_visit
        
        context['has_active_visit'] = has_active_visit_flag
        context['active_visit_for_actions'] = active_visit_for_actions # Use this for the "Close Visit" button


        context['vitals'] = patient.vital_signs.all().order_by('-updated')
        # context['payments'] = patient.patient_payments.all().order_by('-updated')
            # Filter payments with credit method and calculate total credit amount
        payments = patient.patient_payments.all().order_by('-updated')
        context['payments'] = payments

        credit_payments = payments.filter(payment_method='CREDIT')
        total_credit_amount = credit_payments.aggregate(total=Sum('price'))['total'] or 0
        context['total_credit_amount'] = total_credit_amount
        
        context['clinical_notes'] = patient.clinical_notes.all().order_by('-updated')
        context['appointments'] = patient.appointments.all().order_by('-updated')
        context['prescribed_drugs'] = patient.prescribed_drugs.all().order_by('-updated')
        prescribed_drugs = patient.prescribed_drugs.all().order_by('-updated')
        context['prescribed_drugs'] = prescribed_drugs

        context['radiology_results'] = patient.radiology_results.all().order_by('-updated')
        context['physio'] = patient.physio_info.all().order_by('-updated')
        context['admission_info'] = patient.admission_info.all().order_by('-updated')
        context['ward_vital_signs'] = patient.ward_vital_signs.all().order_by('-updated')
        context['ward_medication'] = patient.ward_medication.all().order_by('-updated')
        context['ward_clinical_notes'] = patient.ward_clinical_notes.all().order_by('-updated')
        context['ward_shift_notes'] = patient.ward_shift_notes.all().order_by('-updated')
        context['theatre_bookings'] = patient.theatre_bookings.all().order_by('-updated')
        context['operation_notes'] = patient.operation_notes.all().order_by('-updated')
        context['anaesthesia_checklist'] = patient.anaesthesia_checklist.all().order_by('-updated')

        context['anaesthesia_checklist'] = (patient.anaesthesia_checklist.all().prefetch_related('concurrent_medical_illnesses','past_surgical_history','drug_history','social_history','last_meals').order_by('-updated'))

        context['theatre_operation_record'] = patient.theatre_operation_record.all().order_by('-updated')
        context['surgery_bill'] = patient.surgery_bill.all().order_by('-created')
        context['private_bill'] = patient.private_bill.all().order_by('-created')
        context['archive'] = patient.patient_archive.all().order_by('-updated')

        context['blood_group'] = patient.test_info.filter(bg_test__isnull=False).order_by('-created').select_related('bg_test')
        context['genotype'] = patient.test_info.filter(gt_test__isnull=False).order_by('-created').select_related('gt_test')
        context['fbc'] = patient.test_info.filter(fbc_test__isnull=False).order_by('-created').select_related('fbc_test')

        context['urea_electrolyte'] = patient.test_info.filter(ue_test__isnull=False).order_by('-created').select_related('ue_test')
        context['liver_function'] = patient.test_info.filter(lf_test__isnull=False).order_by('-created').select_related('lf_test')
        context['lipid_profile'] = patient.test_info.filter(lp_test__isnull=False).order_by('-created').select_related('lp_test')
        context['blood_glucose'] = patient.test_info.filter(bgl_test__isnull=False).order_by('-created').select_related('bgl_test')
        context['bone_chemistry'] = patient.test_info.filter(bc_test__isnull=False).order_by('-created').select_related('bc_test')
        context['serum_proteins'] = patient.test_info.filter(sp_test__isnull=False).order_by('-created').select_related('sp_test')
        context['cerebro_spinal_fluid'] = patient.test_info.filter(csf_test__isnull=False).order_by('-created').select_related('csf_test')
        context['miscellaneous_chempath_tests'] = patient.test_info.filter(misc_test__isnull=False).order_by('-created').select_related('misc_test')

        context['widal'] = patient.test_info.filter(widal_test__isnull=False).order_by('-created').select_related('widal_test')
        context['rheumatoid_factor'] = patient.test_info.filter(rheumatoid_factor_test__isnull=False).order_by('-created').select_related('rheumatoid_factor_test')
        context['hpb'] = patient.test_info.filter(hpb_test__isnull=False).order_by('-created').select_related('hpb_test')
        context['hcv'] = patient.test_info.filter(hcv_test__isnull=False).order_by('-created').select_related('hcv_test')
        context['vdrl']= patient.test_info.filter(vdrl_test__isnull=False).order_by('-created').select_related('vdrl_test')
        context['mantoux']= patient.test_info.filter(mantoux_test__isnull=False).order_by('-created').select_related('mantoux_test')
        context['crp']=patient.test_info.filter(crp_test__isnull=False).order_by('-created').select_related('crp_test')
        context['hiv_screening']= patient.test_info.filter(hiv_test__isnull=False).order_by('-created').select_related('hiv_test')
        context['aso_titre'] = patient.test_info.filter(aso_titre_test__isnull=False).order_by('-created').select_related('aso_titre_test')
        
        context['urine_microscopy'] = patient.test_info.filter(urine_test__isnull=False).order_by('-created').select_related('urine_test')
        context['hvs'] = patient.test_info.filter(hvs_test__isnull=False).order_by('-created').select_related('hvs_test')
        context['stool'] = patient.test_info.filter(stool_test__isnull=False).order_by('-created').select_related('stool_test')
        context['blood_culture'] = patient.test_info.filter(blood_culture_test__isnull=False).order_by('-created').select_related('blood_culture_test')
        context['occult_blood'] = patient.test_info.filter(occult_blood_test__isnull=False).order_by('-created').select_related('occult_blood_test')
        context['sputum_mcs'] = patient.test_info.filter(sputum_mcs_test__isnull=False).order_by('-created').select_related('sputum_mcs_test')
        context['gram_stain'] = patient.test_info.filter(gram_stain_test__isnull=False).order_by('-created').select_related('gram_stain_test')
        context['swab_pus_aspirate_mcs'] = patient.test_info.filter(swab_pus_aspirate_test__isnull=False).order_by('-created').select_related('swab_pus_aspirate_test')
        context['zn_stain'] = patient.test_info.filter(zn_stain_test__isnull=False).order_by('-created').select_related('zn_stain_test')
        context['semen_analysis'] = patient.test_info.filter(semen_analysis_test__isnull=False).order_by('-created').select_related('semen_analysis_test')
        context['urinalysis'] = patient.test_info.filter(urinalysis_test__isnull=False).order_by('-created').select_related('urinalysis_test')
        context['pregnancy'] = patient.test_info.filter(pregnancy_test__isnull=False).order_by('-created').select_related('pregnancy_test')



        context['general_results']=patient.test_info.filter(general_results__isnull=False).order_by('-created')
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
        context['prescription_dates'] = prescribed_drugs.dates('prescribed_date', 'day', order='DESC')
  
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
            consultation=True
        ).exists()
        
        if existing_open_visit:
            form.add_error(None, ValidationError(
                _("This patient already has an open/active consultation. Please close the existing visit before creating a new one."),
                code='duplicate_visit'
            ))
            return self.form_invalid(form)
        
        # Create the visit record
        self.object = form.save(commit=False)
        self.object.patient = patient
        self.object.user = self.request.user
        self.object.consultation = True
        
        # Check if this is a review visit
        is_review = (self.object.record and 
                    self.object.record.name and 
                    self.object.record.name.lower() == 'review')
        
        if is_review:
            # BYPASS LOGIC FOR REVIEW VISITS
            self.object.vitals = True  # Skip nursing/vitals
            self.object.review = True  # Mark as review
            self.object.payment = None  # No payment required
            self.object.save()
            
            messages.success(
                self.request, 
                f'Review visit registered for {patient}. Patient sent directly to clinic - no payment or vitals required.'
            )
        else:
            # NORMAL WORKFLOW FOR NEW/FOLLOW-UP VISITS
            self.object.vitals = False
            self.object.review = False
            
            # Create payment record if medical record exists
            if self.object.record:
                payment = Paypoint.objects.create(
                    patient=patient,
                    status=False,
                    service=self.object.record,
                    unit='medical record',
                    price=self.object.record.price,
                )
                self.object.payment = payment
            
            self.object.save()
            
            # Handle payment messaging
            if hasattr(self.object, 'payment') and self.object.payment and self.object.payment.status:
                nursing_desk = NursingDesk.objects.filter(clinic=patient.clinic).first()
                if nursing_desk:
                    messages.success(
                        self.request, 
                        f'Payment successful. Patient sent to {nursing_desk} for vital signs.'
                    )
                else:
                    messages.warning(
                        self.request, 
                        f'Payment successful, but no nursing desk available for {patient.clinic}.'
                    )
            else:
                messages.warning(
                    self.request, 
                    'New visit registered. Proceed to revenue station to complete the payment for the medical record service.'
                )
        
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('patient_list')
# class VisitCreateView(LoginRequiredMixin, CreateView):
#     model = VisitRecord
#     form_class = VisitForm
#     template_name = 'ehr/record/visit.html'
    
    
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['file_no'] = self.kwargs['file_no']
#         return kwargs

#     def form_valid(self, form):
#         patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        
#         # Check for existing open visit
#         existing_open_visit = VisitRecord.objects.filter(
#             patient=patient,
#             # consider if 'consultation=True' is a better check for an "active consultation"
#             consultation=True # Or your existing logic: seen=False 
#         ).exists()

#         if existing_open_visit:
#             form.add_error(None, ValidationError(
#                 _("This patient already has an open/active consultation. Please close the existing visit before creating a new one."),
#                 code='duplicate_visit'
#             ))
#             return self.form_invalid(form)

#         # It's generally better to let CreateView handle setting self.object
#         self.object = form.save(commit=False) # self.object is now the new VisitRecord instance

#         self.object.patient = patient
#         self.object.user = self.request.user
#         self.object.consultation = True  # Ensure new visits are marked as active consultations
#         self.object.vitals = False       # You're already doing this

#         if not self.object.record:
#              pass

#         payment = Paypoint.objects.create(
#             patient=patient,
#             status=False, # Default payment status
#             service=self.object.record, # Make sure self.object.record is populated
#             unit='medical record',
#             price=self.object.record.price, # Make sure self.object.record.price is accessible
#         )
#         self.object.payment = payment
        
#         self.object.save() # Now save the fully populated visit instance with its payment link

#         # Messaging based on payment status
#         if payment.status: # This will be False initially based on Paypoint.objects.create(status=False,...)
#                             # This block might be intended for after a payment update elsewhere.
#             nursing_desk = NursingDesk.objects.filter(clinic=patient.clinic).first()
#             if nursing_desk:
#                 messages.success(self.request, f'Payment successful. Patient sent to {nursing_desk} for vital signs.')
#             else:
#                 messages.warning(self.request, f'Payment successful, but no nursing desk available for {patient.clinic}.')
#         else:
#             messages.warning(self.request, 'New visit registered. Proceed to revenue station to complete the payment for the medical record service.')
        
#         return HttpResponseRedirect(self.get_success_url())
#     def get_success_url(self):
#         return reverse_lazy('patient_list')

class VisitPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/visit_pay_list.html'
    context_object_name = 'visit_pays'
    paginate_by = 20

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(record_payment__isnull=False).order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['payFilter'] = PayFilter(self.request.GET, queryset=self.get_queryset())
        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       
        return context  


class NursingStationDetailView(DetailView):
    model = NursingDesk
    template_name = 'ehr/nurse/nursing_station.html'
    context_object_name = 'nursing_desk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        visits = VisitRecord.objects.filter(
            clinic=self.object.clinic,
            vitals=False  # Just check if they need vitals
        ).select_related('patient', 'payment', 'record')
        query = self.request.GET.get('q')

        if query:
            visits = visits.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )

        # Pass the list of visit records to the template
        context['visits'] = visits
        context['query'] = query or ''

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
        
        # Optimized query with select_related
        visit_record = VisitRecord.objects.filter(
            patient__file_no=self.kwargs['file_no']
        ).select_related('clinic').latest('id')
        
        kwargs['clinic'] = visit_record.clinic
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Optimized query with select_related
        visit_record = VisitRecord.objects.filter(
            patient__file_no=self.kwargs['file_no']
        ).select_related('patient', 'clinic').latest('id')
        
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
        
        # Standardize time filter with other views
        days_filter = 2  # This should match the same value used in VisitListView
        time_threshold = timezone.now() - timedelta(days=days_filter)
        
        for room in rooms:
            room.waiting_count = VisitRecord.objects.filter(
                clinic=self.object,
                room=room,
                vitals=True,
                seen=False,
                updated__gte=time_threshold  # Apply time filter
            ).count()
            
        context['waiting_count'] = VisitRecord.objects.filter(
        clinic=self.object,
        updated__gte=time_threshold).filter(Q(vitals=True, seen=False, review=False) | Q(review=True, seen=False)).count()

        # context['waiting_count'] = VisitRecord.objects.filter(
        #     clinic=self.object,
        #     vitals=True,
        #     seen=False,
        #     review=False,
        #     updated__gte=time_threshold  # Apply time filter
        # ).count()
        
        context['seen_count'] = VisitRecord.objects.filter(
            clinic=self.object,
            seen=True,
            updated__gte=time_threshold  # Apply time filter
        ).count()
        
        context['review_count'] = VisitRecord.objects.filter(
            clinic=self.object,
            review=True,
            updated__gte=time_threshold  # Apply time filter
        ).count()
        
        return context
    
class VisitListView(DoctorNurseRecordRequiredMixin, ListView):
    model = VisitRecord
    template_name = 'ehr/clinic/pt_list.html'  # Base template
    context_object_name = 'visits'
    # filter_params = {}
# For doctor's waiting list, include review patients
    filter_params = {
        'Q(vitals=True, seen=False, review=False) | Q(review=True, seen=False)': True
    }
    def get_queryset(self):
        self.clinic = get_object_or_404(Clinic, pk=self.kwargs['clinic_id'])
        queryset = VisitRecord.objects.filter(
            clinic=self.clinic,
            updated__gte=timezone.now() - timedelta(days=2),
            **self.filter_params
        ).order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__title__icontains=query)|
                Q(patient__phone__icontains=query)
            )
        return queryset
        # return queryset.order_by('-updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic'] = self.clinic
        context['query'] = self.request.GET.get('q', '')        
        return context

class WaitingListView(VisitListView):
    filter_params = {
        'vitals': True,
        'seen': False,
        'review':False
    }
    template_name = 'ehr/clinic/waiting_list.html'  

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

class AppointmentCreateView(RecordRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'ehr/record/new_appointment.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient

        # Get the proposed date and time from the form
        proposed_date = form.cleaned_data.get('date')
        proposed_time = form.cleaned_data.get('time')

        # Check for existing appointments with the same date and time
        conflicting_appointments_exist = Appointment.objects.filter(
            date=proposed_date,
            time=proposed_time
        ).exists()

        # Check if the user has confirmed to override the conflict
        confirm_override = self.request.POST.get('confirm_override')

        if conflicting_appointments_exist and not confirm_override:
            # If there's a conflict and no override confirmation,
            # add a warning and return the form. The template will show the modal.
            messages.warning(self.request, 'APPOINTMENT CONFLICT: An appointment already exists at this exact date and time. Do you want to proceed anyway?')
            return self.render_to_response(self.get_context_data(form=form)) # Render the form to display the message
        else:
            # No conflict, or conflict confirmed to be overridden
            self.object = form.save()
            messages.success(self.request, 'APPOINTMENT ADDED SUCCESSFULLY!')
            return super().form_valid(form)

    def get_success_url(self):
        if hasattr(self, 'object') and self.object:
            return self.object.patient.get_absolute_url()
        return reverse_lazy("appointments")


class AppointmentUpdateView(UpdateView):
    model = Appointment
    template_name = 'ehr/record/update_appt.html'
    form_class = AppointmentForm
    success_url = reverse_lazy("appointments")

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Get the proposed date and time from the form
        proposed_date = form.cleaned_data.get('date')
        proposed_time = form.cleaned_data.get('time')

        # Check for existing appointments with the same date and time, excluding the current appointment
        conflicting_appointments_exist = Appointment.objects.filter(
            date=proposed_date,
            time=proposed_time
        ).exclude(pk=self.object.pk).exists()

        # Check if the user has confirmed to override the conflict
        confirm_override = self.request.POST.get('confirm_override')

        if conflicting_appointments_exist and not confirm_override:
            messages.warning(self.request, 'APPOINTMENT CONFLICT: An appointment already exists at this exact date and time. Do you want to proceed anyway?')
            return self.render_to_response(self.get_context_data(form=form))
        else:
            form.save()
            messages.success(self.request, 'APPOINTMENT UPDATED SUCCESSFULLY!')
            return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating appointment information.')
        return self.render_to_response(self.get_context_data(form=form))    

# class AppointmentCreateView(RecordRequiredMixin, CreateView):
#     model = Appointment
#     form_class = AppointmentForm
#     template_name = 'ehr/record/new_appointment.html'

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
#         self.object = form.save()
#         messages.success(self.request, 'APPOINTMENT ADDED')
        
#         return super().form_valid(form)

#     def get_success_url(self):
#         return self.object.patient.get_absolute_url()

# class AppointmentUpdateView(UpdateView):
#     model = Appointment
#     template_name = 'ehr/record/update_appt.html'
#     form_class = AppointmentForm
#     success_url = reverse_lazy("appointments")

    
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         messages.success(self.request, 'Appointment Updated Successfully')
#         if form.is_valid():
#             form.save()
#             return super().form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, 'Error updating appointment information')
#         return self.render_to_response(self.get_context_data(form=form))

    
class AppointmentListView(ListView):
    model=Appointment
    template_name='ehr/record/appointment.html'
    context_object_name='appointments'
    paginate_by = 20

    def get_queryset(self):
        appointment = super().get_queryset().order_by('-updated')
        appointment_filter = AppointmentFilter(self.request.GET, queryset=appointment)
        return appointment_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointmentFilter'] = AppointmentFilter(self.request.GET, queryset=self.get_queryset())
        return context



class HospitalServicesListView(TemplateView):
    template_name = 'ehr/dashboard/services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active tab from the request
        active_tab = self.request.GET.get('active_tab', 'services')
        context['active_tab'] = active_tab

        # Paginate each queryset
        medical_record_paginator = Paginator(MedicalRecord.objects.all(), 10)
        services_paginator = Paginator(Services.objects.all(), 10)
        lab_test_paginator = Paginator(GenericTest.objects.all(), 10)
        radiology_test_paginator = Paginator(RadiologyTest.objects.all(), 10)
        physio_test_paginator = Paginator(PhysioTest.objects.all(), 10)

        medical_record_page = self.request.GET.get('medical_record_page', 1)
        services_page = self.request.GET.get('services_page', 1)
        lab_test_page = self.request.GET.get('lab_test_page', 1)
        radiology_test_page = self.request.GET.get('radiology_test_page', 1)
        physio_test_page = self.request.GET.get('physio_test_page', 1)

        context['medical_record'] = medical_record_paginator.get_page(medical_record_page)
        context['services'] = services_paginator.get_page(services_page)
        context['lab_test'] = lab_test_paginator.get_page(lab_test_page)
        context['radiology_test'] = radiology_test_paginator.get_page(radiology_test_page)
        context['physio_test'] = physio_test_paginator.get_page(physio_test_page)

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
    """
    View for updating payment information and handling payment processing.
    Supports both AJAX and traditional form submissions.
    """
    model = Paypoint
    template_name = 'ehr/revenue/update_pay.html'
    form_class = PayUpdateForm

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests, with special handling for AJAX requests.
        Returns payment details for AJAX requests, normal form view otherwise.
        """
        self.object = self.get_object()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'payment_method': self.object.payment_method,
                'status': self.object.status,
            }
            return JsonResponse(data)
            
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        """
        Determine the redirect URL after successful form submission.
        Prioritizes 'next' parameter if provided.
        """
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")

    def get_context_data(self, **kwargs):
        """
        Add additional context data for the template.
        Includes patient information, service details, and next URL.
        """
        context = super().get_context_data(**kwargs)
        paypoint = self.get_object()
        
        context.update({
            'patient': paypoint.patient,
            'service': paypoint.service,
            'next': self.request.GET.get('next', reverse_lazy("pay_list"))
        })
        
        return context

    @transaction.atomic
    def form_valid(self, form):
        """
        Process the form if valid. Handles payment processing and wallet updates.
        Uses transaction.atomic to ensure database consistency.
        """
        form.instance.user = self.request.user
        paypoint = form.save(commit=False)
        
        try:
            # Save the payment record
            paypoint.save()
            
            # Handle surgery bill specific logic
            if paypoint.service.startswith("Standard Bill:"):
                wallet, created = Wallet.objects.get_or_create(patient=paypoint.patient)
                wallet.add_funds(paypoint.price)
            
            messages.success(self.request, 'TRANSACTION SUCCESSFUL')
            
            # Determine redirect URL based on payment status
            if paypoint.status:
                redirect_url = f'/revenue/print-receipt/?id={paypoint.id}&next={self.get_success_url()}'
            else:
                redirect_url = self.get_success_url()
            
            # Return appropriate response based on request type
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': redirect_url
                })
            return redirect(redirect_url)
            
        except ValidationError as e:
            error_message = str(e)
            if "Insufficient funds" in error_message:
                error_message = "Insufficient funds in the wallet. Please add funds and try again."
            
            form.add_error(None, error_message)
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Handle invalid form submission.
        Returns JSON response for AJAX requests, normal form response otherwise.
        """
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        return super().form_invalid(form)


class PayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/transaction.html'
    context_object_name = 'pays'
    paginate_by = 50

    def get_queryset(self):
        # Start with an optimized queryset
        queryset = Paypoint.objects.select_related('patient', 'user').order_by('-updated')
        
        # Get filter parameter from URL, default to 'all'
        status_filter = self.request.GET.get('status', 'all')
        
        # Apply status filter if not 'all'
        if status_filter == 'approved':
            queryset = queryset.filter(status=True)
        elif status_filter == 'pending':
            queryset = queryset.filter(status=False)
        
        # Apply other filters from PayFilter
        pay_filter = PayFilter(self.request.GET, queryset=queryset)
        return pay_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the filtered queryset
        filtered_queryset = self.get_queryset()
        
        # Calculate totals based on filtered results
        filtered_summary = filtered_queryset.aggregate(
            total_count=Count('id'),
            approved_count=Count('id', filter=Q(status=True)),
            pending_count=Count('id', filter=Q(status=False)),
            total_worth=Sum('price', filter=Q(status=True)),
            total_pending=Sum('price', filter=Q(status=False))
        )
        
        # Calculate overall database totals (unfiltered)
        overall_summary = Paypoint.objects.aggregate(
            overall_total_count=Count('id'),
            overall_approved_count=Count('id', filter=Q(status=True)),
            overall_pending_count=Count('id', filter=Q(status=False)),
            overall_total_worth=Sum('price', filter=Q(status=True)),
            overall_total_pending=Sum('price', filter=Q(status=False))
        )
        
        context.update({
            # Filtered totals (for current view)
            'total_count': filtered_summary['total_count'],
            'approved_count': filtered_summary['approved_count'],
            'pending_count': filtered_summary['pending_count'],
            'total_worth': filtered_summary['total_worth'] or 0,
            'total_pending': filtered_summary['total_pending'] or 0,
            
            # Overall database totals
            'overall_total_count': overall_summary['overall_total_count'],
            'overall_approved_count': overall_summary['overall_approved_count'],
            'overall_pending_count': overall_summary['overall_pending_count'],
            'overall_total_worth': overall_summary['overall_total_worth'] or 0,
            'overall_total_pending': overall_summary['overall_total_pending'] or 0,
            
            'current_filter': self.request.GET.get('status', 'all'),
            'payFilter': PayFilter(self.request.GET, queryset=self.get_queryset())
        })
        
        # Add date-based metrics using filtered queryset
        today = timezone.now().date()
        context['today_transactions'] = filtered_queryset.filter(created=today).count()
        context['today_worth'] = filtered_queryset.filter(created=today, status=True).aggregate(total=Sum('price'))['total'] or 0
        
        return context

class UnitRevenueView(TemplateView):
    template_name = 'ehr/revenue/unit_revenue.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date
        today = timezone.now().date()
        
        # Calculate current date ranges
        start_of_week = today - timezone.timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        
        current_month = today.month
        current_quarter = (current_month - 1) // 3 + 1
        quarter_start_month = (current_quarter - 1) * 3 + 1
        start_of_quarter = today.replace(month=quarter_start_month, day=1)
        
        start_of_year = today.replace(month=1, day=1)
        
        # Calculate previous date ranges for comparison
        yesterday = today - timezone.timedelta(days=1)
        
        prev_week_start = start_of_week - timezone.timedelta(days=7)
        prev_week_end = start_of_week - timezone.timedelta(days=1)
        
        if start_of_month.month == 1:
            prev_month_start = start_of_month.replace(year=start_of_month.year-1, month=12)
        else:
            prev_month_start = start_of_month.replace(month=start_of_month.month-1)
        prev_month_end = start_of_month - timezone.timedelta(days=1)
        
        if quarter_start_month == 1:
            prev_quarter_start = today.replace(year=today.year-1, month=10, day=1)
        elif quarter_start_month == 4:
            prev_quarter_start = today.replace(month=1, day=1)
        elif quarter_start_month == 7:
            prev_quarter_start = today.replace(month=4, day=1)
        else:  # quarter_start_month == 10
            prev_quarter_start = today.replace(month=7, day=1)
        prev_quarter_end = start_of_quarter - timezone.timedelta(days=1)
        
        prev_year_start = start_of_year.replace(year=start_of_year.year-1)
        prev_year_end = start_of_year - timezone.timedelta(days=1)
        
        # Get all distinct units
        units = Paypoint.objects.filter(status=True).values_list('unit', flat=True).distinct()
        
        # Prepare data structure for units
        unit_revenues = []
        chart_labels = []
        chart_datasets = []
        chart_colors = [
            'rgba(54, 162, 235, 0.8)',  # blue
            'rgba(255, 99, 132, 0.8)',   # red
            'rgba(75, 192, 192, 0.8)',   # green
            'rgba(255, 159, 64, 0.8)',   # orange
            'rgba(153, 102, 255, 0.8)',  # purple
            'rgba(255, 205, 86, 0.8)',   # yellow
            'rgba(201, 203, 207, 0.8)'   # grey
        ]
        
        # Track total revenue by day for the past 30 days
        thirty_days_ago = today - timezone.timedelta(days=30)
        daily_revenues = {}
        
        for i in range(31):
            date = today - timezone.timedelta(days=i)
            daily_revenues[date] = 0
        
        thirty_day_revenue_data = Paypoint.objects.filter(
            status=True, 
            created__gte=thirty_days_ago
        ).values('created').annotate(
            daily_total=Sum('price')
        ).order_by('created')
        
        for entry in thirty_day_revenue_data:
            if entry['created'] in daily_revenues:
                daily_revenues[entry['created']] = float(entry['daily_total'] or 0)
        
        # Payment method distribution
        payment_methods = Paypoint.objects.filter(
            status=True
        ).values('payment_method').annotate(
            total=Sum('price'),
            count=Count('id')
        ).order_by('-total')
        
        # Collect unit data
        color_index = 0
        yearly_dataset = {
            'label': 'Yearly Revenue by Unit',
            'data': [],
            'backgroundColor': []
        }
        
        for unit in units:
            if not unit:  # Skip empty unit names
                continue
                
            # Get base queryset for this unit with approved payments
            unit_qs = Paypoint.objects.filter(unit=unit, status=True)
            
            # Calculate revenue for current periods
            today_revenue = unit_qs.filter(created=today).aggregate(total=Sum('price'))['total'] or 0
            week_revenue = unit_qs.filter(created__gte=start_of_week).aggregate(total=Sum('price'))['total'] or 0
            month_revenue = unit_qs.filter(created__gte=start_of_month).aggregate(total=Sum('price'))['total'] or 0
            quarter_revenue = unit_qs.filter(created__gte=start_of_quarter).aggregate(total=Sum('price'))['total'] or 0
            year_revenue = unit_qs.filter(created__gte=start_of_year).aggregate(total=Sum('price'))['total'] or 0
            all_time_revenue = unit_qs.aggregate(total=Sum('price'))['total'] or 0
            
            # Calculate revenue for previous periods
            yesterday_revenue = unit_qs.filter(created=yesterday).aggregate(total=Sum('price'))['total'] or 0
            prev_week_revenue = unit_qs.filter(created__gte=prev_week_start, created__lte=prev_week_end).aggregate(total=Sum('price'))['total'] or 0
            prev_month_revenue = unit_qs.filter(created__gte=prev_month_start, created__lte=prev_month_end).aggregate(total=Sum('price'))['total'] or 0
            prev_quarter_revenue = unit_qs.filter(created__gte=prev_quarter_start, created__lte=prev_quarter_end).aggregate(total=Sum('price'))['total'] or 0
            prev_year_revenue = unit_qs.filter(created__gte=prev_year_start, created__lte=prev_year_end).aggregate(total=Sum('price'))['total'] or 0
            
            # Calculate growth percentages
            day_growth = self.calculate_growth(today_revenue, yesterday_revenue)
            week_growth = self.calculate_growth(week_revenue, prev_week_revenue)
            month_growth = self.calculate_growth(month_revenue, prev_month_revenue)
            quarter_growth = self.calculate_growth(quarter_revenue, prev_quarter_revenue)
            year_growth = self.calculate_growth(year_revenue, prev_year_revenue)
            
            # Get transaction counts
            today_count = unit_qs.filter(created=today).count()
            week_count = unit_qs.filter(created__gte=start_of_week).count()
            month_count = unit_qs.filter(created__gte=start_of_month).count()
            quarter_count = unit_qs.filter(created__gte=start_of_quarter).count()
            year_count = unit_qs.filter(created__gte=start_of_year).count()
            all_time_count = unit_qs.count()
            
            # Calculate average transaction values
            avg_today = self.calculate_average(today_revenue, today_count)
            avg_week = self.calculate_average(week_revenue, week_count)
            avg_month = self.calculate_average(month_revenue, month_count)
            avg_quarter = self.calculate_average(quarter_revenue, quarter_count)
            avg_year = self.calculate_average(year_revenue, year_count)
            avg_all_time = self.calculate_average(all_time_revenue, all_time_count)
            
            # Payment method distribution for this unit
            unit_payment_methods = unit_qs.values('payment_method').annotate(
                total=Sum('price'),
                count=Count('id')
            ).order_by('-total')
            
            unit_data = {
                'name': unit,
                # Current period revenues
                'today_revenue': today_revenue,
                'week_revenue': week_revenue,
                'month_revenue': month_revenue,
                'quarter_revenue': quarter_revenue,
                'year_revenue': year_revenue,
                'all_time_revenue': all_time_revenue,
                
                # Transaction counts
                'today_count': today_count,
                'week_count': week_count,
                'month_count': month_count,
                'quarter_count': quarter_count,
                'year_count': year_count,
                'all_time_count': all_time_count,
                
                # Growth percentages
                'day_growth': day_growth,
                'week_growth': week_growth,
                'month_growth': month_growth,
                'quarter_growth': quarter_growth,
                'year_growth': year_growth,
                
                # Average transaction values
                'avg_today': avg_today,
                'avg_week': avg_week,
                'avg_month': avg_month,
                'avg_quarter': avg_quarter,
                'avg_year': avg_year,
                'avg_all_time': avg_all_time,
                
                # Payment methods
                'payment_methods': unit_payment_methods,
                
                # Chart color
                'color': chart_colors[color_index % len(chart_colors)]
            }
            
            unit_revenues.append(unit_data)
            
            # Add to chart data
            chart_labels.append(unit)
            yearly_dataset['data'].append(float(year_revenue))
            yearly_dataset['backgroundColor'].append(chart_colors[color_index % len(chart_colors)])
            
            color_index += 1
        
        # Sort units by yearly revenue (highest first)
        unit_revenues.sort(key=lambda x: x['year_revenue'], reverse=True)
        
        # Prepare time series data for trend chart
        trend_labels = []
        trend_data = []
        
        # Sort dates for trend chart
        sorted_dates = sorted(daily_revenues.keys())
        for date in sorted_dates:
            trend_labels.append(date.strftime('%b %d'))
            trend_data.append(daily_revenues[date])
        
        # Calculate overall totals with comparisons
        # Current periods
        total_today = Paypoint.objects.filter(status=True, created=today).aggregate(
            total=Sum('price'), count=Count('id')
        )
        total_week = Paypoint.objects.filter(status=True, created__gte=start_of_week).aggregate(
            total=Sum('price'), count=Count('id')
        )
        total_month = Paypoint.objects.filter(status=True, created__gte=start_of_month).aggregate(
            total=Sum('price'), count=Count('id')
        )
        total_quarter = Paypoint.objects.filter(status=True, created__gte=start_of_quarter).aggregate(
            total=Sum('price'), count=Count('id')
        )
        total_year = Paypoint.objects.filter(status=True, created__gte=start_of_year).aggregate(
            total=Sum('price'), count=Count('id')
        )
        total_all_time = Paypoint.objects.filter(status=True).aggregate(
            total=Sum('price'), count=Count('id')
        )
        
        # Previous periods
        total_yesterday = Paypoint.objects.filter(status=True, created=yesterday).aggregate(
            total=Sum('price'), count=Count('id')
        )
        total_prev_week = Paypoint.objects.filter(status=True, created__gte=prev_week_start, created__lte=prev_week_end).aggregate(
            total=Sum('price'), count=Count('id')
        )
        total_prev_month = Paypoint.objects.filter(status=True, created__gte=prev_month_start, created__lte=prev_month_end).aggregate(
            total=Sum('price'), count=Count('id')
        )
        total_prev_quarter = Paypoint.objects.filter(status=True, created__gte=prev_quarter_start, created__lte=prev_quarter_end).aggregate(
            total=Sum('price'), count=Count('id')
        )
        total_prev_year = Paypoint.objects.filter(status=True, created__gte=prev_year_start, created__lte=prev_year_end).aggregate(
            total=Sum('price'), count=Count('id')
        )
        
        # Calculate growth
        today_growth = self.calculate_growth(
            total_today['total'] or 0, 
            total_yesterday['total'] or 0
        )
        week_growth = self.calculate_growth(
            total_week['total'] or 0, 
            total_prev_week['total'] or 0
        )
        month_growth = self.calculate_growth(
            total_month['total'] or 0, 
            total_prev_month['total'] or 0
        )
        quarter_growth = self.calculate_growth(
            total_quarter['total'] or 0, 
            total_prev_quarter['total'] or 0
        )
        year_growth = self.calculate_growth(
            total_year['total'] or 0, 
            total_prev_year['total'] or 0
        )
        
        # Calculate averages
        avg_today = self.calculate_average(total_today['total'] or 0, total_today['count'] or 0)
        avg_week = self.calculate_average(total_week['total'] or 0, total_week['count'] or 0)
        avg_month = self.calculate_average(total_month['total'] or 0, total_month['count'] or 0)
        avg_quarter = self.calculate_average(total_quarter['total'] or 0, total_quarter['count'] or 0)
        avg_year = self.calculate_average(total_year['total'] or 0, total_year['count'] or 0)
        avg_all_time = self.calculate_average(total_all_time['total'] or 0, total_all_time['count'] or 0)
        
        # Add period data to context
        context.update({
            # Total revenue
            'total_today': total_today['total'] or 0,
            'total_week': total_week['total'] or 0,
            'total_month': total_month['total'] or 0,
            'total_quarter': total_quarter['total'] or 0,
            'total_year': total_year['total'] or 0,
            'total_all_time': total_all_time['total'] or 0,
            
            # Transaction counts
            'count_today': total_today['count'] or 0,
            'count_week': total_week['count'] or 0,
            'count_month': total_month['count'] or 0,
            'count_quarter': total_quarter['count'] or 0,
            'count_year': total_year['count'] or 0,
            'count_all_time': total_all_time['count'] or 0,
            
            # Growth percentages
            'today_growth': today_growth,
            'week_growth': week_growth,
            'month_growth': month_growth,
            'quarter_growth': quarter_growth,
            'year_growth': year_growth,
            
            # Average transaction values
            'avg_today': avg_today,
            'avg_week': avg_week,
            'avg_month': avg_month,
            'avg_quarter': avg_quarter,
            'avg_year': avg_year,
            'avg_all_time': avg_all_time,
            
            # Unit data
            'unit_revenues': unit_revenues,
            
            # Chart data
            'chart_labels': chart_labels,
            'yearly_dataset': yearly_dataset,
            'trend_labels': trend_labels,
            'trend_data': trend_data,
            
            # Payment method distribution
            'payment_methods': payment_methods,
        })
        
        # Define periods for the tab navigation
        context['periods'] = [
            {'id': 'today', 'name': 'Today'},
            {'id': 'week', 'name': 'This Week'},
            {'id': 'month', 'name': 'This Month'},
            {'id': 'quarter', 'name': 'This Quarter'},
            {'id': 'year', 'name': 'This Year'},
            {'id': 'all_time', 'name': 'All Time'}
        ]
        
        return context
    
    def calculate_growth(self, current, previous):
        """Calculate percentage growth between two values"""
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)
    
    def calculate_average(self, total, count):
        """Calculate average transaction value"""
        if count == 0:
            return 0
        return round(total / count, 2)  
# class UnitRevenueView(TemplateView):
#     template_name = 'ehr/revenue/unit_revenue.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Get current date
#         today = timezone.now().date()
        
#         # Calculate date ranges
#         start_of_week = today - timezone.timedelta(days=today.weekday())
#         start_of_month = today.replace(day=1)
        
#         # Calculate start of quarter
#         current_month = today.month
#         current_quarter = (current_month - 1) // 3 + 1
#         quarter_start_month = (current_quarter - 1) * 3 + 1
#         start_of_quarter = today.replace(month=quarter_start_month, day=1)
        
#         # Calculate start of year
#         start_of_year = today.replace(month=1, day=1)
        
#         # Get all distinct units
#         units = Paypoint.objects.filter(status=True).values_list('unit', flat=True).distinct()
#         # Prepare data structure directly accessible in templates without custom filters
#         unit_revenues = []
        
#         for unit in units:
#             if not unit:  # Skip empty unit names
#                 continue
                
#             # Get base queryset for this unit with approved payments
#             unit_qs = Paypoint.objects.filter(unit=unit, status=True)
            
#             # Calculate revenue for different time periods
#             today_revenue = unit_qs.filter(created=today).aggregate(total=Sum('price'))['total'] or 0
#             weekly_revenue = unit_qs.filter(created__gte=start_of_week).aggregate(total=Sum('price'))['total'] or 0
#             monthly_revenue = unit_qs.filter(created__gte=start_of_month).aggregate(total=Sum('price'))['total'] or 0
#             quarterly_revenue = unit_qs.filter(created__gte=start_of_quarter).aggregate(total=Sum('price'))['total'] or 0
#             yearly_revenue = unit_qs.filter(created__gte=start_of_year).aggregate(total=Sum('price'))['total'] or 0
#             all_time_revenue = unit_qs.aggregate(total=Sum('price'))['total'] or 0
            
#             # Count transactions for each period
#             today_count = unit_qs.filter(created=today).count()
#             weekly_count = unit_qs.filter(created__gte=start_of_week).count()
#             monthly_count = unit_qs.filter(created__gte=start_of_month).count()
#             quarterly_count = unit_qs.filter(created__gte=start_of_quarter).count()
#             yearly_count = unit_qs.filter(created__gte=start_of_year).count()
#             all_time_count = unit_qs.count()
            
#             unit_revenues.append({
#                 'name': unit,
#                 'today_revenue': today_revenue,
#                 'today_count': today_count,
#                 'week_revenue': weekly_revenue,
#                 'week_count': weekly_count,
#                 'month_revenue': monthly_revenue,
#                 'month_count': monthly_count,
#                 'quarter_revenue': quarterly_revenue,
#                 'quarter_count': quarterly_count,
#                 'year_revenue': yearly_revenue,
#                 'year_count': yearly_count,
#                 'all_time_revenue': all_time_revenue,
#                 'all_time_count': all_time_count,

#             })
        
#         # Sort units by yearly revenue (highest first)
#         unit_revenues.sort(key=lambda x: x['year_revenue'], reverse=True)
        
#         # Calculate overall totals (flattened for direct template access)
#         total_today = Paypoint.objects.filter(status=True, created=today).aggregate(
#             total=Sum('price'), count=Count('id')
#         )
#         total_week = Paypoint.objects.filter(status=True, created__gte=start_of_week).aggregate(
#             total=Sum('price'), count=Count('id')
#         )
#         total_month = Paypoint.objects.filter(status=True, created__gte=start_of_month).aggregate(
#             total=Sum('price'), count=Count('id')
#         )
#         total_quarter = Paypoint.objects.filter(status=True, created__gte=start_of_quarter).aggregate(
#             total=Sum('price'), count=Count('id')
#         )
#         total_year = Paypoint.objects.filter(status=True, created__gte=start_of_year).aggregate(
#             total=Sum('price'), count=Count('id')
#         )
#         total_all_time = Paypoint.objects.filter(status=True).aggregate(
#             total=Sum('price'), count=Count('id')
#         )
#         # Replace None with 0
#         context['total_today'] = total_today['total'] or 0
#         context['count_today'] = total_today['count'] or 0
#         context['total_week'] = total_week['total'] or 0
#         context['count_week'] = total_week['count'] or 0
#         context['total_month'] = total_month['total'] or 0
#         context['count_month'] = total_month['count'] or 0
#         context['total_quarter'] = total_quarter['total'] or 0
#         context['count_quarter'] = total_quarter['count'] or 0
#         context['total_year'] = total_year['total'] or 0
#         context['count_year'] = total_year['count'] or 0
#         context['total_all_time'] = total_all_time['total'] or 0
#         context['count_all_time'] = total_all_time['count'] or 0
        
#         context['unit_revenues'] = unit_revenues
        
#         # Define periods for the tab navigation
#         context['periods'] = [
#             {'id': 'today', 'name': 'Today'},
#             {'id': 'week', 'name': 'This Week'},
#             {'id': 'month', 'name': 'This Month'},
#             {'id': 'quarter', 'name': 'This Quarter'},
#             {'id': 'year', 'name': 'This Year'},
#             {'id': 'all_time', 'name': 'All Time'}
#         ]
        
#         return context

    
@login_required
def thermal_receipt(request):
    ndate = datetime.now()
    filename = ndate.strftime('Report__%d_%m_%Y__%I_%M%p.pdf')
    base_queryset = Paypoint.objects.filter(status=True)
    
    # Then apply the filter
    f = PayFilter(request.GET, queryset=base_queryset).qs
    patient = f.first().patient if f.exists() else None
    total_price = f.aggregate(total_price=Sum('price'))['total_price']


    label_map = {
        'user': 'STAFF',
        'patient': 'FILE NO',
        'service': 'SERVICE',
        'unit': 'UNIT',
        'created1': 'FROM',
        'created2': 'TO',
    }

    filters_applied = []
    for key, value in request.GET.items():
        if value and key in label_map:
            if "created" in key:
                try:
                    date_obj = datetime.strptime(value, '%Y-%m-%d')
                    value = date_obj.strftime('%d-%m-%Y')
                except ValueError:
                    pass
            filters_applied.append(f"{label_map[key]}: {value.upper()}")

    result = " | ".join(filters_applied)


    template = get_template('ehr/revenue/revenue_report.html')

    # template = get_template('ehr/revenue/thermal_receipt.html')
    html = template.render({
        'f': f,
        'total_price':total_price,
        'patient': patient,
        'result': result,
        'receipt_no': f'RCP-{ndate.strftime("%Y%m%d%H%M%S")}',
        'generated_date': datetime.now().strftime('%d-%m-%Y %H:%M'),
        'user': request.user.username.upper(),
    })

    response = HttpResponse(content_type='application/pdf',headers={'Content-Disposition': f'filename="{filename}"'})
    pisa_status = pisa.CreatePDF(html,dest=response,encoding='utf-8',link_callback=fetch_resources,)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    return response


@login_required
def pharm_receipt(request):
    ndate = datetime.now()
    filename = ndate.strftime('Receipt__%d_%m_%Y__%I_%M%p.pdf')
    
    # Start with pharmacy payments and status=True
    base_queryset = Paypoint.objects.filter(
        pharm_payment__isnull=False,
        status=True
    )
    
    # Then apply the filter
    f = PayFilter(request.GET, queryset=base_queryset).qs
    
    patient = f.first().patient if f.exists() else None
    total_price = f.aggregate(total_price=Sum('price'))['total_price']
    
    # Generate header info
    result = ""
    for key, value in request.GET.items():
        if value:
            result += f" {value.upper()} receipt, Generated on: {ndate.strftime('%d-%B-%Y at %I:%M %p')} By: {request.user.username.upper()}"
    
    # Calculate total price
    template = get_template('ehr/revenue/thermal_receipt.html')
    html = template.render({
        'f': f,
        'total_price': total_price,
        'patient': patient,
        'result': result,
        'receipt_no': f'RCP-{ndate.strftime("%Y%m%d%H%M%S")}',
        'generated_date': datetime.now().strftime('%d-%m-%Y %H:%M'),
        'user': request.user.username.upper(),
    })
    
    # Create PDF with custom options
    response = HttpResponse(
        content_type='application/pdf',
        headers={'Content-Disposition': f'filename="{filename}"'}
    )
    
    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        encoding='utf-8',
        link_callback=fetch_resources,
    )
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response


@login_required
def record_receipt(request):
    ndate = datetime.now()
    filename = ndate.strftime('Receipt__%d_%m_%Y__%I_%M%p.pdf')
    
    base_queryset = Paypoint.objects.filter(record_payment__isnull=False,status=True)
    
    f = PayFilter(request.GET, queryset=base_queryset).qs
    
    patient = f.first().patient if f.exists() else None
    total_price = f.aggregate(total_price=Sum('price'))['total_price']
    
    # Generate header info
    result = ""
    for key, value in request.GET.items():
        if value:
            result += f" {value.upper()} receipt, Generated on: {ndate.strftime('%d-%B-%Y at %I:%M %p')} By: {request.user.username.upper()}"
    
    # Calculate total price
    template = get_template('ehr/revenue/thermal_receipt.html')
    html = template.render({
        'f': f,
        'total_price': total_price,
        'patient': patient,
        'result': result,
        'receipt_no': f'RCP-{ndate.strftime("%Y%m%d%H%M%S")}',
        'generated_date': datetime.now().strftime('%d-%m-%Y %H:%M'),
        'user': request.user.username.upper(),
    })
    
    # Create PDF with custom options
    response = HttpResponse(
        content_type='application/pdf',
        headers={'Content-Disposition': f'filename="{filename}"'}
    )
    
    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        encoding='utf-8',
        link_callback=fetch_resources,
    )
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response

def format_currency(amount):
    if amount is None:
        return "N0.00"
    return f"N{amount:,.2f}"


# FOR NORMAL PAYMENT
def print_receipt_pdf(request):
    ndate = datetime.now()
    payment_id = request.GET.get('id')
    payment = get_object_or_404(Paypoint, id=payment_id)
    patient = payment.patient
    
    # Prepare context for the template
    context = {
        'receipt_no': f'RCP-{ndate.strftime("%Y%m%d%H%M%S")}',
        'payment': payment,
        'patient': patient,
        'total': payment.price or 0,
        'generated_date': datetime.now().strftime('%d-%m-%Y %H:%M'),
        'user': request.user.username.upper(),
    }
    
    # Render the template
    template = get_template('ehr/revenue/receipt.html')
    html = template.render(context)
    
    # Create PDF
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    
    if not pisa_status.err:
        buffer.seek(0)
        ndate = datetime.now()
        filename = ndate.strftime('on__%d_%m_%Y_at_%I_%M%p.pdf')
        return HttpResponse(
            buffer.getvalue(),
            content_type='application/pdf',
            headers={'Content-Disposition': f'inline; filename="Receipt__{filename}"'}
        )
    
    return HttpResponse('Error generating PDF', status=500)
    

class AdmissionCreateView(RevenueRequiredMixin, CreateView):
    model = Admission
    form_class = AdmissionForm
    template_name = 'ehr/ward/new_admission.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient
        
        # Calculate number of days between admission and expected discharge
        expected_date = form.instance.expected_discharge_date
        admission_date = date.today()
        if expected_date:
            # Add 1 to include both the admission day and discharge day
            days_count = (expected_date - admission_date).days + 1
            # Ensure we don't have negative days
            days_count = max(days_count, 1)
        else:
            # Default to 1 day if no expected discharge date is provided
            days_count = 1
        
        admission_fee = form.save(commit=False)
        
        # Handle case where ward price might be missing
        # We assume ward exists but check to be safe
        if not admission_fee.ward:
            # This shouldn't happen if form validation is correct, but just in case
            raise ValueError("Ward is required for admission")
            
        ward_name = admission_fee.ward.name
        # Safely get ward price - default to 0 if None
        ward_price = getattr(admission_fee.ward, 'price', 0) or 0
        
        payment = Paypoint.objects.create(
            patient=patient,
            status=False,
            service=f"{ward_name} admission Fees",
            unit='admission',
            # Safely calculate price
            price=ward_price * days_count,
        )
        
        admission_fee.payment = payment
        admission_fee.save()
        return super().form_valid(form)
        
    def get_success_url(self):
        messages.success(self.request, 'PATIENT ADMITTED')
        return self.object.patient.get_absolute_url()

        
class AdmissionListView(ListView):
    model=Admission
    template_name='ehr/ward/admission_list.html'
    context_object_name='admissions'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(payment__status__isnull=False)
        # Add search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__title__icontains=query)|
                Q(patient__phone__icontains=query)
            )

        return queryset.order_by('-updated')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')        
        return context


class AdmissionPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/admission_pay_list.html'
    context_object_name = 'admission_pays'
    paginate_by = 20

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(admission_payment__isnull=False).order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       
        return context  
     

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
    def get_success_url(self):
        return self.object.patient.get_absolute_url()


class WardMedicationCreateView(NurseRequiredMixin,CreateView):
    model = WardMedication
    form_class = WardMedicationForm
    template_name = 'ehr/ward/ward_medication.html'

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

    def get_success_url(self):
        return self.object.patient.get_absolute_url()


class WardNotesCreateView(NurseRequiredMixin,CreateView):
    model = WardClinicalNote
    form_class = WardNotesForm
    template_name = 'ehr/ward/ward_notes.html'

    def get_success_url(self):
        return self.object.patient.get_absolute_url()

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        messages.success(self.request, 'Notes Taken')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context

class WardNotesUpdateView(NurseRequiredMixin, UpdateView):
    model=WardClinicalNote
    form_class = WardNotesForm
    template_name = 'ehr/ward/ward_notes.html'
    
    def get_success_url(self):
        messages.success(self.request, 'NOTES UPDATED')
        return self.object.patient.get_absolute_url()


class WardShiftNotesCreateView(NurseRequiredMixin,CreateView):
    model = WardShiftNote
    form_class = WardShiftNotesForm
    template_name = 'ehr/ward/ward_notes.html'

    def form_valid(self, form):
        form.instance.nurse = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        messages.success(self.request, 'Notes Taken')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context

    def get_success_url(self):
        return self.object.patient.get_absolute_url()


class WardShiftNotesUpdateView(NurseRequiredMixin, UpdateView):
    model=WardShiftNote
    form_class = WardShiftNotesForm
    template_name = 'ehr/ward/ward_notes.html'
    
    def get_success_url(self):
        messages.success(self.request, 'NOTES UPDATED')
        return self.object.patient.get_absolute_url()
    

class RadiologyResultCreateView(LoginRequiredMixin, CreateView):
    model = RadiologyResult
    form_class = RadiologyResultForm
    template_name = 'ehr/radiology/radiology_result.html'

    def form_valid(self, form):
        patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient
        form.instance.user = self.request.user
        radiology_result = form.save(commit=False)
        radiology_result.save()

        messages.success(self.request, 'Radiology test created successfully')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('all_radiology_req')
    

class RadiologyListView(ListView):
    model=RadiologyResult
    template_name='ehr/radiology/radiology_list.html'
    context_object_name='radiology_results'

    def get_queryset(self):
        queryset = super().get_queryset().filter(cleared=True).order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')       
        return context  
    

class RadiologyRequestListView(ListView):
    model=RadiologyResult
    template_name='ehr/radiology/radiology_request.html'
    context_object_name='radiology_request'

    def get_queryset(self):
        queryset = super().get_queryset().filter(cleared=False).order_by('-updated')

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')       
        return context  


@method_decorator(login_required(login_url='login'), name='dispatch')
class RadioReportView(ListView):
    model = RadiologyResult
    template_name = 'ehr/radiology/radiology_report.html'
    paginate_by = 20
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
    

class RadiologyPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/radiology_pay_list.html'
    context_object_name = 'radiology_pays'
    paginate_by = 20

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(radiology_payment__isnull=False).order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       
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
        patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        context['patient'] = patient
        
        # Check for theatre booking before form submission
        latest_theatre_booking = (
            TheatreBooking.objects
            .filter(patient=patient)
            .order_by('-date', '-id')
            .distinct()
            .first()
        )

        if not latest_theatre_booking:
            messages.warning(
                self.request,
                'No theatre booking found for this patient. Please add theatre booking details first. by click the calendar icon below'
            )
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
        
        # Use a fresh queryset and explicitly select the latest booking
        latest_theatre_booking = (
            TheatreBooking.objects
            .filter(patient=patient)
            .order_by('-date', '-id')  # Add secondary sort on ID to break ties
            .distinct()
            .first()
        )
        bill = Bill.objects.create(
            user=self.request.user, 
            patient=patient,
            theatre_booking=latest_theatre_booking
        )
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
            service=f"Standard Bill:-{bill.id}",
            unit='surgery bill',
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
        context['billing_items'] = Billing.objects.filter(bill=self.object).select_related('item', 'item__category')
        
        # Add theatre booking context with fallback to None
        theatre_booking = getattr(self.object, 'theatre_booking', None)
        context.update({
            'theatre_booking': theatre_booking,
            'diagnosis': theatre_booking.diagnosis if theatre_booking else None,
            'operation_planned': theatre_booking.operation_planned if theatre_booking else None,
            'team': theatre_booking.team if theatre_booking else None,
            'theatre': theatre_booking.theatre if theatre_booking else None,
            'booking_date': theatre_booking.date if theatre_booking else None
        })
        
        return context

    def get_queryset(self):
        return super().get_queryset().prefetch_related('items__item__category')
# class BillDetailView(DetailView):
#     model = Bill
#     template_name = 'ehr/revenue/bill_detail.html'
#     context_object_name = 'bill'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['billing_items'] = Billing.objects.filter(bill=self.object).select_related('item', 'item__category')
#         return context
    
#     def get_queryset(self):
#         return super().get_queryset().prefetch_related('items__item__category')


class BillingPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/bill_pay_list.html'
    context_object_name = 'bill_pays'
    paginate_by = 20

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(service__startswith='Standard Bill:-').order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        
        pay_total = queryset.count()
        total_worth = queryset.filter(status=True).aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       
        return context


class BillListView(DoctorRequiredMixin, LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'ehr/revenue/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 20

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
                content = f"inline; filename={filename}"
                response['Content-Disposition'] = content
            return response
        return HttpResponse("Error generating PDF", status=400)
    

class TheatreBookingCreateView(DoctorRequiredMixin, CreateView):
    model = TheatreBooking
    form_class = TheatreBookingForm
    template_name = 'ehr/theatre/book_theatre.html'

    def form_valid(self, form):
        form.instance.doctor = self.request.user
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
    

class TheatreBookingListView(DoctorRequiredMixin, ListView):
    model = TheatreBooking
    template_name = 'ehr/theatre/theatre_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 20

    def get_queryset(self):
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)

        # Get patients who have been operated
        operated_patients = OperationNotes.objects.filter(
            operated=True, 
            theatre=theatre
        ).values_list('patient', flat=True)

        # Filter out theatre bookings for operated patients
        theatrebooking = super().get_queryset().filter(
            theatre=theatre
        ).exclude(
            patient__in=operated_patients
        ).order_by('-updated')

        theatrebooking_filter = TheatreBookingFilter(self.request.GET, queryset=theatrebooking)
        return theatrebooking_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)

        total_bookings = self.get_queryset().count()
        
        context['theatre'] = theatre
        context['total_bookings'] = total_bookings
        context['theatreBookingFilter'] = TheatreBookingFilter(
            self.request.GET, 
            queryset=self.get_queryset()
        )
        return context

class OperationNotesCreateView(DoctorRequiredMixin,CreateView):
    model = OperationNotes
    form_class = OperationNotesForm
    template_name = 'ehr/theatre/theatre_notes.html'

    def form_valid(self, form):
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        theatre_booking = TheatreBooking.objects.filter(patient=patient_data).order_by('-id').first()
        if theatre_booking:
            form.instance.theatre = theatre_booking.theatre
        
        form.instance.doctor = self.request.user
        form.instance.patient = patient_data
        self.object = form.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context

    def get_success_url(self):
        messages.success(self.request, 'PATIENT OPERATION NOTES ADDED')
        return self.object.patient.get_absolute_url()


class OperationNotesListView(DoctorRequiredMixin,ListView):
    model=OperationNotes
    template_name='ehr/theatre/operated_list.html'
    context_object_name='operated'
    paginate_by = 20

    def get_queryset(self):
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)

        operate_note = OperationNotes.objects.filter(operated=True, theatre=theatre).order_by('-updated')
        theatre_filter = OperationNotesFilter(self.request.GET, queryset=operate_note)
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


class OperationNotesUpdateView(DoctorRequiredMixin, UpdateView):
    model=OperationNotes
    form_class = OperationNotesForm
    template_name = 'ehr/theatre/theatre_notes.html'
    
    def get_success_url(self):
        messages.success(self.request, 'NOTES UPDATED')
        return self.object.patient.get_absolute_url()


ConcurrentMedicalIllnessFormSet = inlineformset_factory(
    AnaesthesiaChecklist,
    ConcurrentMedicalIllness,
    form=ConcurrentMedicalIllnessForm,
    extra=3
)
PastSurgicalHistoryFormSet = inlineformset_factory(
    AnaesthesiaChecklist,
    PastSurgicalHistory,
    form=PastSurgicalHistoryForm,
    extra=3
)

DrugHistoryFormSet = inlineformset_factory(
    AnaesthesiaChecklist,
    DrugHistory,
    form=DrugHistoryForm,
    extra=3
)

SocialHistoryFormSet = inlineformset_factory(
    AnaesthesiaChecklist,
    SocialHistory,
    form=SocialHistoryForm,
    extra=3
)
LastMealFormSet = inlineformset_factory(
    AnaesthesiaChecklist,
    LastMeal,
    form=LastMealForm,
    extra=3
)

class AnaesthesiaChecklistCreateView(LoginRequiredMixin, CreateView):
    model = AnaesthesiaChecklist
    form_class = AnaesthesiaChecklistForm
    template_name = 'ehr/theatre/anaesthesia_checklist.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if self.request.method == 'POST':
            data['concurrent_medical_illness_formset'] = ConcurrentMedicalIllnessFormSet(self.request.POST)
            data['past_surgical_history_formset'] = PastSurgicalHistoryFormSet(self.request.POST)
            data['drug_history_formset'] = DrugHistoryFormSet(self.request.POST)
            data['social_history_formset'] = SocialHistoryFormSet(self.request.POST)
            data['last_meal_formset'] = LastMealFormSet(self.request.POST)
        else:
            data['concurrent_medical_illness_formset'] = ConcurrentMedicalIllnessFormSet()
            data['past_surgical_history_formset'] = PastSurgicalHistoryFormSet()
            data['drug_history_formset'] = DrugHistoryFormSet()
            data['social_history_formset'] = SocialHistoryFormSet()
            data['last_meal_formset'] = LastMealFormSet()

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        concurrent_medical_illness_formset = context['concurrent_medical_illness_formset']
        past_surgical_history_formset = context['past_surgical_history_formset']
        drug_history_formset = context['drug_history_formset']
        social_history_formset = context['social_history_formset']
        last_meal_formset = context['last_meal_formset']

        form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.doctor = self.request.user

        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])

        admission_info = Admission.objects.filter(patient=patient_data).order_by('-id').first()
        if admission_info:
            form.instance.ward = admission_info.ward

        theatre_booking = TheatreBooking.objects.filter(patient=patient_data).order_by('-id').first()
        if theatre_booking:
            form.instance.theatre = theatre_booking.theatre
            form.instance.patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])

        self.object = form.save()

        if concurrent_medical_illness_formset.is_valid():
            concurrent_medical_illness_formset.instance = self.object
            concurrent_medical_illness_formset.save()

        if past_surgical_history_formset.is_valid():
            past_surgical_history_formset.instance = self.object
            past_surgical_history_formset.save()
        else:
            # Display more specific error messages
            messages.error(self.request, 'Past Surgical History form is not valid:')
            for error in past_surgical_history_formset.errors:
                messages.error(self.request, error)
            for form in past_surgical_history_formset:
                for field, error in form.errors.items():
                    messages.error(self.request, f'{field}: {error}')

            return self.render_to_response(self.get_context_data())

        if drug_history_formset.is_valid():
            drug_history_formset.instance = self.object
            drug_history_formset.save()
        else:
            # Display more specific error messages
            messages.error(self.request, 'Drug History form is not valid:')
            for error in drug_history_formset.errors:
                messages.error(self.request, error)
            for form in drug_history_formset:
                for field, error in form.errors.items():
                    messages.error(self.request, f'{field}: {error}')
       
        if social_history_formset.is_valid():
            social_history_formset.instance = self.object
            social_history_formset.save()
        else:
            # Display more specific error messages
            messages.error(self.request, 'Social History form is not valid:')
            for error in social_history_formset.errors:
                messages.error(self.request, error)
            for form in social_history_formset:
                for field, error in form.errors.items():
                    messages.error(self.request, f'{field}: {error}')

        if last_meal_formset.is_valid():
            last_meal_formset.instance = self.object
            last_meal_formset.save()
        else:
            # Display more specific error messages
            messages.error(self.request, 'Last Meal form is not valid:')
            for error in last_meal_formset.errors:
                messages.error(self.request, error)
            for form in last_meal_formset:
                for field, error in form.errors.items():
                    messages.error(self.request, f'{field}: {error}')

            return self.render_to_response(self.get_context_data())

        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'SUCCESSFULLY ADDED')
        return self.object.patient.get_absolute_url()        


class AnaesthesiaChecklistListView(DoctorRequiredMixin,ListView):
    model = AnaesthesiaChecklist
    template_name = 'ehr/theatre/anaesthesia_checklist_list.html'
    context_object_name = 'anaesthesia_checklists'
    paginate_by = 20

    def get_queryset(self):
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)
        queryset = super().get_queryset().filter(theatre=theatre).order_by('-updated')
        
        # Apply filter if GET parameters exist
        if self.request.GET:
            f = AnaesthesiaChecklistFilter(self.request.GET, queryset=queryset)
            return f.qs
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        theatre_id = self.kwargs.get('theatre_id')
        theatre = get_object_or_404(Theatre, id=theatre_id)
        total_operations = self.get_queryset().count()

        # Add filter to context
        f = AnaesthesiaChecklistFilter(self.request.GET, queryset=self.get_queryset())
        context['anaesthesia_checklistFilter'] = f

        context['total_operations'] = total_operations
        context['theatre'] = theatre
        return context


class AnaesthesiaChecklistDetailView(DetailView):
    model = AnaesthesiaChecklist
    template_name = 'ehr/theatre/anaesthesia_checklist_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['concurrent_medical_illnesses'] = self.object.concurrent_medical_illnesses.all()
        context['past_surgical_histories'] = self.object.past_surgical_history.all()
        context['drug_histories'] = self.object.drug_history.all()
        context['social_histories'] = self.object.social_history.all()
        context['last_meals'] = self.object.last_meals.all()
        return context


class PrivateBillingCreateView(DoctorRequiredMixin,LoginRequiredMixin,  FormView):
    template_name = 'ehr/revenue/private_billing.html'
    
    def get_form(self):
        PrivateBillingFormSet = modelformset_factory(PrivateBilling, form=PrivateBillingForm, extra=25)
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
            service=f"Quick Surgery Bill:-{private_bill.id}",
            unit='Quick Bill',
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
                
        return context
        

class PrivateBillingPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/private_bill_pay_list.html'
    context_object_name = 'private_bill_pays'
    paginate_by = 20

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")

        
    def get_queryset(self):
        queryset = super().get_queryset().filter(service__startswith='Quick Surgery Bill:-').order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        pay_total = queryset.count()
        total_worth = queryset.filter(status=True).aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       

        return context


class PrivateBillListView(DoctorRequiredMixin, LoginRequiredMixin, ListView):
    model = PrivateBill
    template_name = 'ehr/revenue/private_bill_list.html'
    context_object_name = 'private_bills'
    paginate_by = 20

    def get_queryset(self):
        return PrivateBill.objects.filter(user=self.request.user).prefetch_related('private_items').order_by('-created')

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
                content = f"inline; filename={filename}"
                response['Content-Disposition'] = content
            return response
        return HttpResponse("Error generating PDF", status=400) 


class FundWalletView(RevenueRequiredMixin,CreateView):
    model = WalletTransaction
    form_class = FundWalletForm
    template_name = 'ehr/revenue/fund_wallet.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(pk=self.kwargs['patient_pk'])
        return context
    
    def get_success_url(self):
        # return reverse_lazy('patient_details', kwargs={'file_no': self.object.wallet.patient.file_no})
        return reverse_lazy('patient_wallet_list')

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
    paginate_by = 20 

    def get_queryset(self):
        return WalletTransaction.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_credit'] = WalletTransaction.objects.filter(transaction_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_debit'] = WalletTransaction.objects.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or 0
        context['net_balance'] = context['total_credit'] - context['total_debit']
        return context
    

class TheatreOperationRecordCreateView(DoctorNurseRecordRequiredMixin,CreateView):
    model = TheatreOperationRecord
    form_class = TheatreOperationRecordForm
    template_name = 'ehr/theatre/theatre_record.html'
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'consumableusage_set__consumable',
            'implantusage_set__implant'
        )

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
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])

        admission_info = Admission.objects.filter(patient=patient_data).order_by('-id').first()
        if admission_info:
            form.instance.ward = admission_info.ward

        theatre_booking = TheatreBooking.objects.filter(patient=patient_data).order_by('-id').first()
        if theatre_booking:
            form.instance.theatre = theatre_booking.theatre

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
        # self.object=form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'SURGERY RECORD ADDED')
        return self.object.patient.get_absolute_url()


class TheatreOperationRecordDetailView(DoctorNurseRecordRequiredMixin,DetailView):
    model = TheatreOperationRecord
    template_name = 'ehr/theatre/theatre_record_details.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            Prefetch('consumableusage_set', queryset=ConsumableUsage.objects.select_related('consumable')),
            Prefetch('implantusage_set', queryset=ImplantUsage.objects.select_related('implant'))
        )

class TheatreOperationRecordListView(DoctorRequiredMixin, ListView):
    model = TheatreOperationRecord
    template_name = 'ehr/theatre/theatre_record_list.html'
    context_object_name = 'surgical_records'
    paginate_by = 20

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
        

class PhysioTestCreateView(DoctorRequiredMixin, CreateView):
    model = PhysioRequest
    form_class = PhysioRequestForm
    template_name = 'ehr/physio/physio_form.html'
        
    def form_valid(self, form):
        patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient
        form.instance.doctor = self.request.user

        physio_test = form.save(commit=False)
        payment = Paypoint.objects.create(
            patient=patient,
            status=False,
            service=physio_test.test.name,
            unit='physiotherapy',
            price=physio_test.test.price,
        )
        physio_test.payment = payment 
        physio_test.save()
        
        messages.success(self.request, 'physio request created successfully')
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.patient.get_absolute_url()


class PhysioListView(ListView):
    model=PhysioRequest
    template_name='ehr/physio/physio_list.html'
    context_object_name='physio'

    def get_queryset(self):
        queryset = super().get_queryset().filter(payment__status__isnull=False,cleared=True).order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')       
        return context 
    

class PhysioRequestUpdateView(PhysioRequiredMixin, UpdateView):
    model = PhysioRequest
    form_class = PhysioResultForm
    template_name = 'ehr/physio/physio_form.html'
    success_url=reverse_lazy('physio_request')

    def get_object(self, queryset=None):
        patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        return get_object_or_404(PhysioRequest, patient=patient, pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.physiotherapist = self.request.user
        physio_request = form.save(commit=False)
        physio_request.save()
        messages.success(self.request, 'Physiotherapy result updated successfully')
        return super().form_valid(form)


class PhysioRequestListView(ListView):
    model=PhysioRequest
    template_name='ehr/physio/physio_request.html'
    context_object_name='physio'

    def get_queryset(self):
        queryset = super().get_queryset().filter(cleared=False).order_by('-updated')

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')       
        return context  


@method_decorator(login_required(login_url='login'), name='dispatch')
class PhysioReportView(ListView):
    model = PhysioRequest
    template_name = 'ehr/physio/physio_report.html'
    paginate_by = 20
    context_object_name = 'patient'

    def get_queryset(self):
        queryset = super().get_queryset()

        physio_filter = PhysioFilter(self.request.GET, queryset=queryset)
        patient = physio_filter.qs.order_by('-updated')
        return patient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['physio_filter'] = PhysioFilter(self.request.GET, queryset=self.get_queryset())
        return context
    

class PhysioPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/physio_pay_list.html'
    context_object_name = 'physio_pays'
    paginate_by = 20

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(physio_payment__isnull=False).order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       
        return context


class CreditPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/credit_pay_list.html'
    context_object_name = 'credit_pays'
    paginate_by = 20

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(payment_method='CREDIT').order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       
        return context


class CashPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/cash_pay_list.html'
    context_object_name = 'cash_pays'
    paginate_by = 20

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(payment_method='CASH').order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       
        return context
    

class RadiologyInvestigationsCreateView(DoctorRequiredMixin, FormView):
    template_name = 'ehr/radiology/radiology_req_form.html'
    form_class = RadiologyInvestigationsForm

    def get_form(self):
        RadiologyInvestigationsFormSet = modelformset_factory(
            RadiologyInvestigations,
            form=RadiologyInvestigationsForm,
            extra=10
        )
        if self.request.method == 'POST':
            return RadiologyInvestigationsFormSet(self.request.POST)
        return RadiologyInvestigationsFormSet(queryset=RadiologyInvestigations.objects.none())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_form()
        context['patient'] = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        return context

    def post(self, request, *args, **kwargs):
        formset = self.get_form()
        print("POST Data:", request.POST)  # Debug print
        print("Formset is valid:", formset.is_valid())  # Debug print
        if not formset.is_valid():
            print("Formset errors:", formset.errors)  # Debug print
        if formset.is_valid():
            return self.formset_valid(formset)
        return self.formset_invalid(formset)

    @transaction.atomic
    def formset_valid(self, formset):
        patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])

        radiologytest = RadiologyTests.objects.create(
            user=self.request.user,
            patient=patient,
        )
        total_amount = 0
        instances = formset.save(commit=False)

        for instance in instances:
            if instance.item:
                instance.radiologytest = radiologytest
                total_amount += instance.item.price
                instance.save()

        radiologytest.total_amount = total_amount
        radiologytest.save()

        paypoint = Paypoint.objects.create(
            user=self.request.user,
            patient=patient,
            service=f"Radiology Investigation",
            unit='radiology',
            price=total_amount,
            status=False
        )
        radiologytest.payment = paypoint
        radiologytest.save()

        messages.success(self.request, 'RADIOLOGY REQUEST ADDED')
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_success_url(self):
        return reverse('patient_details', kwargs={'file_no': self.kwargs['file_no']})


from django.db.models import Prefetch
class RadiologyTestDetailView(DetailView):
    model = RadiologyTests
    template_name = 'ehr/radiology/radiology_req_details.html'
    context_object_name = 'tests'  # Changed to match your template

    def get_queryset(self):
        return RadiologyTests.objects.select_related(
            'user',
            'patient',
        ).prefetch_related(
            Prefetch(
                'radiology_items',
                queryset=RadiologyInvestigations.objects.select_related(
                    'item',
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['radiology_items'] = self.object.radiology_items.all()
        return context

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), 
        result,
        encoding='UTF-8'
    )
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class RadiologyTestPDFView(DetailView):
    model = RadiologyTests
    template_name = 'ehr/radiology/radiology_pdf.html'
    
    def get_queryset(self):
        return RadiologyTests.objects.select_related(
            'user',
            'patient'
        ).prefetch_related(
            Prefetch(
                'radiology_items',
                queryset=RadiologyInvestigations.objects.select_related('item',)
            )
        )

    def get(self, request, *args, **kwargs):
        radiologytest = self.get_object()
        radiology_items = radiologytest.radiology_items.all()
        
        context = {
            'radiologytest': radiologytest,
            'radiology_items': radiology_items,
            'generated_date': datetime.now().strftime('%d-%m-%Y %H:%M'),
            'doc_title': 'RADIOLOGY REQUEST',
        }
        
        pdf = render_to_pdf(self.template_name, context)
        
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            if 'download' in request.GET:
                filename = f"RADIOLOGY_REQ_{radiologytest.patient.file_no}_{datetime.now().strftime('%Y%m%d')}.pdf"
                response['Content-Disposition'] = f'inline; filename="{filename}"'
            else:
                response['Content-Disposition'] = 'inline'
            return response
            
        return HttpResponse("Error Generating PDF", status=500)
    

class AllRadiologyTestListView(LoginRequiredMixin, ListView):
    model = RadiologyTests
    template_name = 'ehr/radiology/incoming_radiology_req.html'
    context_object_name = 'tests'
    paginate_by = 20  # Adjust as needed
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-updated')
    # rest of your code remains the same
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class RadiologyUpdateView(LoginRequiredMixin, UpdateView):
    model = RadiologyResult
    form_class = RadiologyUpdateResultForm
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

        # New View to manually close a visit
@method_decorator(login_required(login_url='login'), name='dispatch')
class CloseVisitView(DoctorRequiredMixin, View): # Or a more general permission mixin
    def post(self, request, *args, **kwargs):
        patient_file_no = self.kwargs.get('file_no')
        visit_pk = self.kwargs.get('visit_pk')
        
        # Ensure the visit belongs to the patient and exists
        visit_to_close = get_object_or_404(VisitRecord, pk=visit_pk, patient__file_no=patient_file_no)
        patient = get_object_or_404(PatientData, file_no=patient_file_no) # To redirect back

        # Optional: Add more specific permission checks if needed (e.g., only the assigned doctor)

        if visit_to_close.consultation:
            visit_to_close.close_visit() # Calls your model's method
            messages.success(request, f"Visit (ID: {visit_to_close.pk}) for {patient} has been successfully closed.")
        else:
            messages.info(request, f"Visit (ID: {visit_to_close.pk}) for {patient} was already closed.")
        
        return redirect(patient.get_absolute_url()) # Redirect back to patient folder

# --- Your ClinicalNoteCreateView ---
# Consider if the dispatch logic should also check for active consultation
@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicalNoteCreateView(DoctorRequiredMixin, CreateView):
    model = ClinicalNote
    form_class = ClinicalNoteForm
    template_name = 'ehr/doctor/clinical_note.html'
    
    def dispatch(self, request, *args, **kwargs):
        patient_data = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        
        # Current logic: Checks if *any* visit record exists.
        # visit = VisitRecord.objects.filter(patient=patient_data).order_by('-id').first()
        # if visit is None:
        # messages.error(request, f'Cannot create clinical note for {patient_data.first_name} {patient_data.last_name} ({patient_data.file_no}). No visit record found...')
        # return redirect(patient_data.get_absolute_url())

        # Suggested alternative: Check for an *active* visit if notes can only be added to active ones.
        active_visit = VisitRecord.objects.filter(patient=patient_data, consultation=True).order_by('-id').first()
        if active_visit is None:
            messages.error(
                request, 
                f'Cannot create clinical note for {patient_data.first_name} {patient_data.last_name} ({patient_data.file_no}). No active consultation found. Please ensure the patient has an ongoing visit that is not yet closed.'
            )
            return redirect(patient_data.get_absolute_url())
        
        self.active_visit = active_visit # Store for use in form_valid
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        patient_data = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        # self.object = form.save() # Save later after visit update or if needed before

        # Use the active_visit identified in dispatch
        # visit = VisitRecord.objects.filter(patient=patient_data).order_by('-id').first()
        visit = self.active_visit # Use the one from dispatch

        # It's good practice to ensure 'visit' is not None here, though dispatch should handle it.
        if not visit:
             messages.error(self.request, "Error: Could not find the associated visit record.")
             return redirect(patient_data.get_absolute_url())

        # Save the clinical note first
        self.object = form.save()

        if form.instance.needs_review:
            visit.review = True
            visit.seen = True 
            visit.save(update_fields=['review', 'seen']) # Be specific about fields to update
            messages.success(self.request, f'Clinical note for {patient_data.first_name} {patient_data.last_name} created. Patient awaiting review.')
        else:
            # visit.close_visit() # This method handles setting consultation=False, seen=True, review=False and saving.
            messages.success(self.request, f'Clinical note for {patient_data.first_name} {patient_data.last_name} created. Patient consultation completed.')
        
        # The super().form_valid(form) typically handles saving the object and redirection.
        # Since we saved `self.object` and handled messages, we might just need to redirect.
        # However, CreateView's form_valid expects to return an HttpResponse.
        # return redirect(self.get_success_url()) # Original super().form_valid would do this.
        return super().form_valid(form) # Let CreateView handle the rest if self.object is set.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        context['patient'] = patient
        context['active_visit'] = getattr(self, 'active_visit', None) # Pass active visit to template if needed
        return context

    def get_success_url(self):
        # Ensure self.object is set (form.save() does this)
        if self.object:
            return self.object.patient.get_absolute_url()
        # Fallback if self.object isn't set, though it should be
        patient_data = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        return patient_data.get_absolute_url()

# --- Your ClinicalNoteUpdateView ---
# Similar considerations for using the latest active visit if updates should only happen on active ones.
@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicalNoteUpdateView(DoctorRequiredMixin, UpdateView):
    model = ClinicalNote
    template_name = 'ehr/doctor/update_clinical_note.html'
    form_class = ClinicalNoteUpdateForm # Assuming ClinicalNoteUpdateForm exists
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        clinical_note = self.get_object()
        patient_data = clinical_note.patient
        
        # form.instance.patient = patient_data # Not needed if patient is not a field in the form being changed
        self.object = form.save() # Save clinical note changes
        
        # Get the latest active visit record for this patient to update its status
        # If notes can be updated even for closed visits, then fetch latest overall.
        # If updates should only affect status of an *active* visit:
        visit = VisitRecord.objects.filter(patient=patient_data, consultation=True).order_by('-id').first()
        
        # If you want to update the status of the visit associated at the time of note creation (even if now closed),
        # you might need to link ClinicalNote directly to a VisitRecord, or fetch based on creation time proximity.
        # For now, let's assume we act on the *current latest active visit* if one exists.

        if visit: 
            if form.instance.needs_review:
                visit.review = True
                visit.seen = False
                visit.save(update_fields=['review',])
                # visit.save(update_fields=['review', 'seen'])
                messages.success(self.request, f'Clinical note for {patient_data.first_name} {patient_data.last_name} updated. Patient awaiting review.')
            else:
                # visit.close_visit()
                messages.success(self.request, f'Clinical note for {patient_data.first_name} {patient_data.last_name} updated. Patient consultation completed.')
        else:
            # No active visit found to update status for, but the note itself is updated.
            messages.success(self.request, f'Clinical note for {patient_data.first_name} {patient_data.last_name} updated successfully. (No active visit to modify status for).')
        
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return self.object.patient.get_absolute_url()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinical_note = self.get_object()
        context['patient'] = clinical_note.patient
        # Optionally, pass the relevant visit if needed in the template
        # context['visit_associated_with_note'] = VisitRecord.objects.filter(patient=clinical_note.patient, consultation=True).order_by('-id').first()
        return context

from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from datetime import timedelta, datetime
from collections import defaultdict, Counter
import json
from django.db.models.functions import ExtractWeekDay, ExtractHour, TruncMonth
from django.db.models import Count, Avg, Q # Q is already used, Count, Avg are good to have grouped
from django.utils import timezone # already used
from datetime import timedelta # already used
from django.contrib.auth.models import User
from .models import PatientData, ClinicalNote, VisitRecord, Clinic, Team

class AnalyticsView(TemplateView):
    template_name = 'analytics.html'

class ComprehensiveAnalyticsView(TemplateView):
    template_name = 'ehr/analytics/comprehensive_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date and time periods
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        six_months_ago = now - timedelta(days=180)
        
        # ============ DOCTOR ANALYTICS ============
        context.update(self._get_doctor_analytics(today_start, week_start, month_start, year_start))
        
        # ============ DIAGNOSIS ANALYTICS ============
        context.update(self._get_diagnosis_analytics(six_months_ago))
        
        # ============ PATIENT DEMOGRAPHICS ============ 
        context.update(self._get_patient_demographics())
        
        # ============ GEOGRAPHIC ANALYTICS ============
        context.update(self._get_geographic_analytics())
        
        # ============ CLINICAL WORKFLOW ============
        context.update(self._get_clinical_workflow_analytics(month_start))
        
        # ============ TRENDS AND PATTERNS ============
        context.update(self._get_trends_analytics(six_months_ago))
        
        # ============ KEY PERFORMANCE INDICATORS ============
        context.update(self._get_kpi_metrics())
        
        return context
    
    def _get_doctor_analytics(self, today_start, week_start, month_start, year_start):
        """Analytics focused on individual doctor performance"""
        doctors = User.objects.filter(
            Q(clinicalnote__isnull=False) | Q(visitrecord__isnull=False)
        ).distinct()
        
        doctor_stats = []
        for doctor in doctors:
            # Clinical notes by doctor
            notes_all = ClinicalNote.objects.filter(user=doctor)
            notes_today = notes_all.filter(updated__gte=today_start)
            notes_week = notes_all.filter(updated__gte=week_start)
            notes_month = notes_all.filter(updated__gte=month_start)
            notes_year = notes_all.filter(updated__gte=year_start)
            
            # Visits handled by doctor
            visits_all = VisitRecord.objects.filter(seen_by=doctor, seen=True) if hasattr(VisitRecord, 'seen_by') else VisitRecord.objects.none()
            visits_today = visits_all.filter(updated__gte=today_start)
            visits_week = visits_all.filter(updated__gte=week_start)
            visits_month = visits_all.filter(updated__gte=month_start)
            visits_year = visits_all.filter(updated__gte=year_start)
            
            # Unique patients seen
            unique_patients_all = notes_all.values('patient').distinct().count()
            unique_patients_month = notes_month.values('patient').distinct().count()
            
            # Diagnoses made
            diagnoses_all = notes_all.exclude(diagnosis__isnull=True).exclude(diagnosis__exact='')
            top_diagnoses = diagnoses_all.values('diagnosis').annotate(
                count=Count('diagnosis')
            ).order_by('-count')[:5]
            
            # Notes needing review
            pending_review = notes_all.filter(needs_review=True).count()
            
            doctor_stats.append({
                'doctor': doctor,
                'notes': {
                    'total': notes_all.count(),
                    'today': notes_today.count(),
                    'this_week': notes_week.count(),
                    'this_month': notes_month.count(),
                    'this_year': notes_year.count(),
                },
                'visits': {
                    'total': visits_all.count(),
                    'today': visits_today.count(),
                    'this_week': visits_week.count(),
                    'this_month': visits_month.count(),
                    'this_year': visits_year.count(),
                },
                'unique_patients': {
                    'total': unique_patients_all,
                    'this_month': unique_patients_month,
                },
                'diagnoses': {
                    'total': diagnoses_all.count(),
                    'top_diagnoses': list(top_diagnoses),
                },
                'pending_review': pending_review,
                'productivity_score': self._calculate_doctor_productivity_score(
                    notes_month.count(), unique_patients_month, pending_review
                )
            })
        
        # Sort by productivity score
        doctor_stats.sort(key=lambda x: x['productivity_score'], reverse=True)
        
        return {
            'doctor_stats': doctor_stats,
            'total_doctors': len(doctor_stats)
        }
    
    def _calculate_doctor_productivity_score(self, notes_count, unique_patients, pending_review):
        """Calculate a simple productivity score for doctors"""
        score = (notes_count * 2) + (unique_patients * 3) - (pending_review * 1)
        return max(0, score)  # Ensure non-negative
    
    def _get_diagnosis_analytics(self, six_months_ago):
        """Analytics for diagnoses and clinical patterns"""
        all_notes = ClinicalNote.objects.exclude(diagnosis__isnull=True).exclude(diagnosis__exact='')
        recent_notes = all_notes.filter(updated__gte=six_months_ago)
        
        # Most common diagnoses
        common_diagnoses = all_notes.values('diagnosis').annotate(
            count=Count('diagnosis')
        ).order_by('-count')[:20]
        
        # Diagnosis trends over time (monthly)
        diagnosis_trends = recent_notes.annotate(
            month=TruncMonth('updated')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Diagnosis by age groups
        age_groups = {
            'age_0_18': all_notes.filter(patient__age__lt=18).count(),
            'age_19_35': all_notes.filter(patient__age__gte=19, patient__age__lte=35).count(),
            'age_36_50': all_notes.filter(patient__age__gte=36, patient__age__lte=50).count(),
            'age_51_65': all_notes.filter(patient__age__gte=51, patient__age__lte=65).count(),
            'age_65_plus': all_notes.filter(patient__age__gt=65).count(),
        }
        
        # Diagnosis by gender
        diagnosis_by_gender = {
            'male': all_notes.filter(patient__gender='MALE').count(),
            'female': all_notes.filter(patient__gender='FEMALE').count(),
        }
        
        # Seasonal patterns (by month)
        seasonal_patterns = all_notes.annotate(
            month=TruncMonth('updated')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return {
            'common_diagnoses': list(common_diagnoses),
            'diagnosis_trends': list(diagnosis_trends),
            'diagnosis_age_groups': age_groups,
            'diagnosis_by_gender': diagnosis_by_gender,
            'seasonal_patterns': list(seasonal_patterns),
            'total_diagnoses': all_notes.count()
        }
    
    def _get_patient_demographics(self):
        """Patient demographic analytics"""
        all_patients = PatientData.objects.all()
        
        # Age distribution
        age_distribution = {
    'age_0_18': all_patients.filter(age__lt=18).count(),
    'age_19_35': all_patients.filter(age__gte=19, age__lte=35).count(),
    'age_36_50': all_patients.filter(age__gte=36, age__lte=50).count(),
    'age_51_65': all_patients.filter(age__gte=51, age__lte=65).count(),
    'age_65_plus': all_patients.filter(age__gt=65).count(),
}
        # Gender distribution
        gender_distribution = all_patients.values('gender').annotate(
            count=Count('gender')
        ).order_by('-count')
        
        # Marital status
        marital_status = all_patients.values('marital_status').annotate(
            count=Count('marital_status')
        ).order_by('-count')
        
        # Religion distribution
        religion_distribution = all_patients.values('religion').annotate(
            count=Count('religion')
        ).order_by('-count')
        
        # Occupation categories (top 15)
        occupation_stats = all_patients.exclude(
            occupation__isnull=True
        ).exclude(
            occupation__exact=''
        ).values('occupation').annotate(
            count=Count('occupation')
        ).order_by('-count')[:15]
        
        # Nationality breakdown
        nationality_stats = all_patients.values('nationality').annotate(
            count=Count('nationality')
        ).order_by('-count')
        
        return {
            'age_distribution': age_distribution,
            'gender_distribution': list(gender_distribution),
            'marital_status': list(marital_status),
            'religion_distribution': list(religion_distribution),
            'occupation_stats': list(occupation_stats),
            'nationality_stats': list(nationality_stats),
        }
    
    def _get_geographic_analytics(self):
        """Geographic distribution analytics"""
        all_patients = PatientData.objects.all()
        
        # Geopolitical zone distribution
        zone_distribution = all_patients.values('zone').annotate(
            count=Count('zone')
        ).order_by('-count')
        
        # State distribution (top 20)
        state_distribution = all_patients.values('state').annotate(
            count=Count('state')
        ).order_by('-count')[:20]
        
        # LGA distribution (top 20)
        lga_distribution = all_patients.values('lga').annotate(
            count=Count('lga')
        ).order_by('-count')[:20]
        
        # Tribal distribution (top 15)
        tribal_distribution = all_patients.exclude(
            tribe__isnull=True
        ).exclude(
            tribe__exact=''
        ).values('tribe').annotate(
            count=Count('tribe')
        ).order_by('-count')[:15]
        
        return {
            'zone_distribution': list(zone_distribution),
            'state_distribution': list(state_distribution),
            'lga_distribution': list(lga_distribution),
            'tribal_distribution': list(tribal_distribution),
        }
    
    def _get_clinical_workflow_analytics(self, month_start):
        """Clinical workflow and efficiency analytics"""
        all_notes = ClinicalNote.objects.all()
        recent_notes = all_notes.filter(updated__gte=month_start)

        # Notes requiring review
        review_stats = {
            'total_pending': all_notes.filter(needs_review=True).count(),
            'pending_this_month': recent_notes.filter(needs_review=True).count(),
            'completed_reviews': all_notes.filter(needs_review=False).count(),
        }

        # Notes creation patterns by day of week
        notes_by_weekday = recent_notes.annotate(
            weekday=ExtractWeekDay('updated')  # Django handles DB-specifics
        ).values('weekday').annotate(
            count=Count('id')
        ).order_by('weekday')

        # Notes creation patterns by hour
        notes_by_hour = recent_notes.annotate(
            hour=ExtractHour('updated')  # Django handles DB-specifics
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')

        # Average notes per patient
        avg_notes_per_patient = all_notes.values('patient').annotate(
            note_count=Count('id')
        ).aggregate(
            avg_notes=Avg('note_count')
        )['avg_notes'] or 0

        # Documentation completeness
        total_patients = PatientData.objects.count()
        # Ensure your PatientData model has a related_name like 'clinical_notes' for this reverse lookup
        # If not, this query might need adjustment, e.g. PatientData.objects.filter(clinicalnote__isnull=False)
        patients_with_notes = PatientData.objects.filter(
            clinical_notes__isnull=False # Assuming 'clinical_notes' is the related_name from ClinicalNote.patient
        ).distinct().count()

        documentation_rate = (patients_with_notes / total_patients * 100) if total_patients > 0 else 0

        return {
            'review_stats': review_stats,
            'notes_by_weekday': list(notes_by_weekday),
            'notes_by_hour': list(notes_by_hour),
            'avg_notes_per_patient': round(avg_notes_per_patient, 2),
            'documentation_rate': round(documentation_rate, 2),
        }
    
    def _get_trends_analytics(self, six_months_ago):
        """Trend analysis for growth and patterns"""
        # Patient registration trends
        patient_trends_qs = PatientData.objects.filter(
            # Ensure 'created' field exists and is a DateTimeField or DateField
            updated__gte=six_months_ago # Optional: if you want to limit trends to a period
        )
        if hasattr(PatientData, 'created'):
            patient_trends = patient_trends_qs.annotate(
                month=TruncMonth('created') # Django handles DB-specifics
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            patient_trends = list(patient_trends)
        else:
            patient_trends = []

        # Clinical notes trends
        notes_trends = ClinicalNote.objects.filter(
            updated__gte=six_months_ago
        ).annotate(
            month=TruncMonth('updated')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        # Growth calculations
        current_month_patients = 0
        if hasattr(PatientData, 'created'):
            current_month_patients = PatientData.objects.filter(
                created__gte=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            ).count()

        return {
            'patient_trends': patient_trends,
            'notes_trends': list(notes_trends),
            'current_month_patients': current_month_patients,
        }
    
    def _get_kpi_metrics(self):
        """Key Performance Indicators"""
        total_patients = PatientData.objects.count()
        total_notes = ClinicalNote.objects.count()
        notes_with_diagnosis = ClinicalNote.objects.exclude(
            diagnosis__isnull=True
        ).exclude(diagnosis__exact='').count()
        
        # Calculate various KPIs
        diagnosis_completion_rate = (notes_with_diagnosis / total_notes * 100) if total_notes > 0 else 0
        
        # Patient contact completeness
        complete_contacts = PatientData.objects.exclude(phone__isnull=True).exclude(phone__exact='').count()
        contact_completion_rate = (complete_contacts / total_patients * 100) if total_patients > 0 else 0
        
        # NOK information completeness
        complete_nok = PatientData.objects.exclude(nok_name__isnull=True).exclude(nok_name__exact='').count()
        nok_completion_rate = (complete_nok / total_patients * 100) if total_patients > 0 else 0
        
        return {
            'kpi_metrics': {
                'diagnosis_completion_rate': round(diagnosis_completion_rate, 1),
                'contact_completion_rate': round(contact_completion_rate, 1),
                'nok_completion_rate': round(nok_completion_rate, 1),
                'avg_notes_per_patient': round(total_notes / total_patients, 2) if total_patients > 0 else 0,
            }
        }


# Additional view for doctor-specific detailed analytics
class DoctorDetailAnalyticsView(TemplateView):
    template_name = 'ehr/analytics/doctor_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor_id = kwargs.get('doctor_id')

        try:
            doctor = User.objects.get(id=doctor_id)
            context['doctor'] = doctor

            # Detailed analytics for specific doctor
            notes = ClinicalNote.objects.filter(user=doctor)

            # Monthly performance over last 12 months
            twelve_months_ago = timezone.now() - timedelta(days=365)
            monthly_performance = notes.filter(
                updated__gte=twelve_months_ago
            ).annotate(
                month=TruncMonth('updated')
            ).values('month').annotate(
                notes_count=Count('id'),
                unique_patients=Count('patient', distinct=True),
                diagnoses_made=Count('diagnosis', filter=Q(diagnosis__isnull=False))
            ).order_by('month')

            context['monthly_performance'] = list(monthly_performance)

            # Top diagnoses by this doctor
            top_diagnoses = notes.exclude(
                diagnosis__isnull=True
            ).exclude(
                diagnosis__exact=''
            ).values('diagnosis').annotate(
                count=Count('diagnosis')
            ).order_by('-count')[:10]

            context['top_diagnoses'] = list(top_diagnoses)

            # Patient demographics for this doctor
            doctor_patients = PatientData.objects.filter(clinical_notes__user=doctor).distinct()

            context['doctor_patient_demographics'] = {
                'total_patients': doctor_patients.count(),
                'gender_breakdown': doctor_patients.values('gender').annotate(count=Count('gender')),
                'age_groups': {
                    # CHANGE THESE KEYS:
                    'age_0_18': doctor_patients.filter(age__lt=18).count(),
                    'age_19_35': doctor_patients.filter(age__gte=19, age__lte=35).count(),
                    'age_36_50': doctor_patients.filter(age__gte=36, age__lte=50).count(),
                    'age_51_plus': doctor_patients.filter(age__gt=50).count(),
                }
            }

        except User.DoesNotExist:
            context['error'] = 'Doctor not found'

        return context


from django.db.models import Count, Q
from datetime import date
from django.shortcuts import render
from .models import PatientData, Ward, Theatre, TheatreBooking, OperationNotes # Assuming your models are in .models
# Don't forget to import reverse if you use it directly in the view, though for template urls, it's not needed here
# from django.urls import reverse

def hospital_dashboard_optimized(request):
    """
    Optimized version using database aggregation for better performance
    """
    today = date.today()

    # Overall Statistics
    total_patients = PatientData.objects.count()
    total_wards = Ward.objects.count()
    total_theatres = Theatre.objects.count()
    operations_today = TheatreBooking.objects.filter(date=today).count()

    # Ward Statistics with aggregation and sorting
    ward_stats = Ward.objects.annotate(
        total_admitted=Count('admission'),
        currently_admitted=Count('admission', filter=Q(admission__status='ADMIT')),
        received_patients=Count('admission', filter=Q(admission__status='RECEIVED')),
        discharged_patients=Count('admission', filter=Q(admission__status='DISCHARGE'))
    ).values(
        'id', 'name', 'total_admitted', 'currently_admitted',
        'received_patients', 'discharged_patients'
    ).order_by('name')

    # Theatre Statistics with aggregation
    theatre_stats = Theatre.objects.annotate(
        bookings_today=Count('theatrebooking', filter=Q(theatrebooking__date=today)),
        operations_completed=Count('operationnotes', filter=Q(operationnotes__operated=True)),
        total_operations=Count('operationnotes')
    ).values(
        'id','name', 'bookings_today', 'operations_completed', 'total_operations'
    ).order_by('name')

    # Calculate pending operations for each theatre
    for theatre in theatre_stats:
        theatre_obj = Theatre.objects.get(name=theatre['name'])

        # Get unique patients with bookings
        booked_patients = set(TheatreBooking.objects.filter(
            theatre=theatre_obj
        ).values_list('patient', flat=True))

        # Get unique patients with completed operations
        completed_patients = set(OperationNotes.objects.filter(
            theatre=theatre_obj,
            operated=True
        ).values_list('patient', flat=True))

        theatre['operations_pending'] = len(booked_patients - completed_patients)

    # Calculate summary totals
    total_bookings_today = sum(t['bookings_today'] for t in theatre_stats)
    total_operations_completed = sum(t['operations_completed'] for t in theatre_stats)
    total_operations_pending = sum(t['operations_pending'] for t in theatre_stats)
    total_theatre_operations = sum(t['total_operations'] for t in theatre_stats)

    context = {
        'today': today,
        'total_patients': total_patients,
        'total_wards': total_wards,
        'total_theatres': total_theatres,
        'operations_today': operations_today,
        'ward_stats': ward_stats, # Now sorted by name
        'theatre_stats': theatre_stats,
        'total_bookings_today': total_bookings_today,
        'total_operations_completed': total_operations_completed,
        'total_operations_pending': total_operations_pending,
        'total_theatre_operations': total_theatre_operations,
    }

    return render(request, 'ehr/analytics/hospital_dashboard.html', context)