from multiprocessing import context
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from .models import *
from .forms import *
from .filters import *
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime
from django.conf import settings
import os
from django.db.models import Count
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, FormView, ListView, DetailView, UpdateView
from pathology.models import *
from pathology.views import *
User = get_user_model()
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType


def log_anonymous_required(view_function, redirect_to=None):
    if redirect_to is None:
        redirect_to = '/'
    return user_passes_test(lambda u: not u.is_authenticated, login_url=redirect_to)(view_function)


# @login_required
# def fetch_resources(uri, rel):
#     """
#     Handles fetching static and media resources when generating the PDF.
#     """
#     if uri.startswith(settings.STATIC_URL):
#         path = os.path.join(settings.STATIC_ROOT,
#                             uri.replace(settings.STATIC_URL, ""))
#     else:
#         path = os.path.join(settings.MEDIA_ROOT,
#                             uri.replace(settings.MEDIA_URL, ""))
#     return path


@method_decorator(log_anonymous_required, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('get_started')
        else:
            return reverse_lazy('profile_folder', args=[self.request.user.profile.unit])


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
    success_url = reverse_lazy('get_started')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profileform'] = ProfileForm(instance=self.object.profile)
        return context

    def form_valid(self, form):
        userform = UserForm(self.request.POST, instance=self.object)
        profileform = ProfileForm(
            self.request.POST, instance=self.object.profile)

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
    # template_name = "index.html"
    template_name = "get_started.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class GetStartedView(TemplateView):
    template_name = "get_started.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class StaffDashboardView(TemplateView):
    template_name = "staff.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class MedicalRecordView(TemplateView):
    template_name = "ehr/dashboard/medical_record.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class PatientMovementView(TemplateView):
    template_name = "ehr/record/patient_moves.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class RevenueView(TemplateView):
    template_name = "ehr/dashboard/revenue.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class RevenueRecordView(TemplateView):
    template_name = "ehr/revenue/record_revenue.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class NursingView(TemplateView):
    template_name = "ehr/dashboard/nursing.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicDashView(TemplateView):
    template_name = "ehr/dashboard/clinic_list.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicView(TemplateView):
    template_name = "ehr/record/clinic.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class RoomView(TemplateView):
    template_name = "ehr/record/room.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicBaseView(TemplateView):
    template_name = "ehr/record/clinic.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class RadiologyView(TemplateView):
    template_name = "ehr/dashboard/radiology.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class PhatologyView(TemplateView):
    template_name = "ehr/dashboard/phatology.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class PharmacyView(TemplateView):
    template_name = "ehr/dashboard/pharmacy.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class PhysioView(TemplateView):
    template_name = "ehr/dashboard/physio.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class TheatreView(TemplateView):
    template_name = "ehr/dashboard/theatre.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class WardView(TemplateView):
    template_name = "ehr/dashboard/ward.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class ICUView(TemplateView):
    template_name = "ehr/dashboard/icu.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class AuditView(TemplateView):
    template_name = "ehr/dashboard/audit.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class ServiceView(TemplateView):
    template_name = "ehr/dashboard/service.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class TransactionView(TemplateView):
    template_name = "ehr/dashboard/transaction.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class AEClinicDetailView(TemplateView):
    template_name = 'ehr/clinic/ae_details.html'


@method_decorator(login_required(login_url='login'), name='dispatch')
class SOPDClinicDetailView(TemplateView):
    template_name = 'ehr/clinic/sopd_details.html'



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


#1 Patient create
class PatientCreateView(RecordRequiredMixin, CreateView):
    model = PatientData
    form_class = PatientForm
    template_name = 'ehr/record/new_patient.html'
    success_url = reverse_lazy("medical_record")

    def form_valid(self, form):
        patient = form.save()
        PatientHandover.objects.create(patient=patient, clinic='A & E', status='waiting_for_payment')
        messages.success(self.request, 'Patient created successfully')
        return super().form_valid(form)

class UpdatePatientView(UpdateView):
    model = PatientData
    template_name = 'ehr/record/update_patient.html'
    form_class = PatientForm

    def get_success_url(self):
        messages.success(self.request, 'Patient Information Updated Successfully')
        return self.object.get_absolute_url()

    def form_valid(self, form):
        if form.is_valid():
            form.save()
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
        patients = super().get_queryset().order_by('-updated')
        patient_filter = PatientFilter(self.request.GET, queryset=patients)
        return patient_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_patient = self.get_queryset().count()
        context['patientFilter'] = PatientFilter(self.request.GET, queryset=self.get_queryset())
        context['total_patient'] = total_patient
        return context


class PatientReportView(ListView):
    model=PatientData
    template_name='ehr/report/patient_report.html'
    context_object_name='patients'
    paginate_by = 10

    def get_queryset(self):
        patients = super().get_queryset().order_by('-updated')
        patient_report_filter = PatientReportFilter(self.request.GET, queryset=patients)
        return patient_report_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_patient = self.get_queryset().count()
        context['patientReportFilter'] = PatientReportFilter(self.request.GET, queryset=self.get_queryset())
        context['total_patient'] = total_patient
        return context
    

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
        context['clinical_notes'] = patient.clinical_notes.all().order_by('-updated')
        context['hematology_results']=patient.hematology_result.all().order_by('-created')
        context['chempath_results']=patient.chemical_pathology_results.all().order_by('-created')
        context['micro_results']=patient.microbiology_results.all().order_by('-created')
        context['serology_results']=patient.serology_results.all().order_by('-created')
        context['general_results']=patient.general_results.all().order_by('-created')

        return context

# 2. FollowUpVisitCreateView
class FollowUpVisitCreateView(RecordRequiredMixin, CreateView):
    model = FollowUpVisit
    form_class = VisitForm
    template_name = 'ehr/record/follow_up.html'
    success_url = reverse_lazy("medical_record")

    def get_object(self, queryset=None):
        file_no = self.kwargs.get('file_no')
        return PatientData.objects.get(file_no=file_no)

    def form_valid(self, form):
        patient = self.get_object()
        visit = form.save(commit=False)
        visit.patient = patient
        visit.save()

        clinic = form.cleaned_data['clinic']

        # Check if a PatientHandover object exists for the patient and clinic
        patient_handover, _ = PatientHandover.objects.get_or_create(
            patient=patient,
            clinic=clinic,
            defaults={'status': 'waiting_for_payment'}
        )

        messages.success(self.request, 'Follow-up visit created successfully')
        return redirect(self.success_url)


class PaypointDashboardView(RevenueRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/revenue/paypoint_dash.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status__in=['waiting_for_payment'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PaypointFollowUpDashboardView(RevenueRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/revenue/follow_up_pay_dash.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        # Get all follow-up visits waiting for payment
        follow_up_visits = FollowUpVisit.objects.filter(patient__handovers__status='waiting_for_payment')

        # Get distinct clinic choices from these follow-up visits
        clinic_choices = follow_up_visits.values_list('clinic', flat=True).distinct()

        # Filter PatientHandover objects based on clinics with follow-up visits waiting for payment
        return PatientHandover.objects.filter(
            status='waiting_for_payment',  # Only include handovers waiting for payment
            clinic__in=clinic_choices
        )

    
class PaypointView(RevenueRequiredMixin, CreateView):
    model=Paypoint
    template_name = 'ehr/revenue/paypoint.html'
    form_class = PaypointForm
    success_url = reverse_lazy("revenue")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        handover = patient.handovers.filter(clinic='A & E', status='waiting_for_payment').first()

        if handover:
            context['patient'] = patient
            context['handover'] = handover
            service_name = 'new registration'
            service = Services.objects.get(name=service_name)
            context['service_name'] = service.name
            context['service_price'] = service.price
        else:
            # Handle the case where no handover object is found
            pass

        return context

    def form_valid(self, form):
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        handover = patient.handovers.filter(clinic='A & E', status='waiting_for_payment').first()

        if handover:
            new_registration_service = Services.objects.get(name='new registration')
            payment = Paypoint.objects.create(patient=patient, status='paid', service=new_registration_service)
            
            # Update handover status to 'waiting_for_vital_signs'
            handover.status = 'waiting_for_vital_signs'
            handover.save()
            messages.success(self.request, 'Payment successful. Patient handed over for vital signs.')
        
        return super().form_valid(form)


class PaypointFollowUpView(RevenueRequiredMixin, CreateView):
    model=Paypoint
    template_name = 'ehr/revenue/paypoint_follow_up.html'
    form_class = PaypointForm
    success_url = reverse_lazy("revenue")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_no = self.kwargs.get('file_no')
        context['patient'] = get_object_or_404(PatientData, file_no=file_no)
        service_name = 'follow up'
        service = Services.objects.get(name=service_name)
        context['service_name'] = service.name
        context['service_price'] = service.price

        return context

    def form_valid(self, form):
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        follow_up_service = Services.objects.get(name='follow up')
        payment = Paypoint.objects.create(patient=patient, status='paid', service=follow_up_service)
        
        # Update handover status to 'waiting_for_vital_signs'
        patient_handover = patient.handovers.filter(status='waiting_for_payment').first()
        if patient_handover:
            patient_handover.status = 'waiting_for_vital_signs'
            patient_handover.save()
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
            patient_handover.status = 'waiting_for_consultation'
            patient_handover.clinic = patient_handover.clinic
            patient_handover.room = form.cleaned_data['handover_room']
            patient_handover.save()

        # If there are no existing handovers, create a new one
        if not patient_handovers.exists():
            PatientHandover.objects.create(patient=patient_data, status='waiting_for_consultation')
        messages.success(self.request, 'Vitals taken, Patient handed over for consultation')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context

    
###BASECLINIC###
class ClinicListView(DoctorRequiredMixin, ListView):
    model = PatientHandover
    context_object_name = 'handovers'

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {
            'status': self.status_filter,
            'clinic': self.clinic_filter,
        }
        if self.room_filter is not None:
            filters['room'] = self.room_filter
        return queryset.filter(**filters)


class AENursingDeskView(ClinicListView):
    template_name = 'ehr/nurse/ae_nursing_desk.html'
    status_filter = 'waiting_for_vital_signs'
    clinic_filter = "A & E"
    room_filter = None


class SOPDNursingDeskView(ClinicListView):
    template_name = 'ehr/nurse/sopd_nursing_desk.html'
    status_filter = 'waiting_for_vital_signs'
    clinic_filter = "SOPD"
    room_filter = None

class AEConsultationWaitRoomView(ClinicListView):
    template_name = 'ehr/clinic/ae_list.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "A & E"
    room_filter = None

class AERoom1View(ClinicListView):
    template_name = 'ehr/clinic/ae_room1.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "A & E"
    room_filter = 'ROOM 1'


class AERoom2View(ClinicListView):
    template_name = 'ehr/clinic/ae_room2.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "A & E"
    room_filter = 'ROOM 2'


class SOPDConsultationWaitRoomView(ClinicListView):
    template_name = 'ehr/clinic/sopd_list.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "SOPD"
    room_filter = None

class SOPDRoom1View(ClinicListView):
    template_name = 'ehr/clinic/sopd_room1.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "SOPD"
    room_filter = 'ROOM 1'


class SOPDRoom2View(ClinicListView):
    template_name = 'ehr/clinic/sopd_room2.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "SOPD"
    room_filter = 'ROOM 2'


@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicalNoteCreateView(CreateView, DoctorRequiredMixin):
    model = ClinicalNote
    form_class = ClinicalNoteForm
    template_name = 'ehr/doctor/clinical_note.html'


    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        self.object = form.save()
        clinic_name = self.request.GET.get('clinic')
        patient_handovers = PatientHandover.objects.filter(patient=form.instance.patient,clinic=clinic_name)
        for patient_handover in patient_handovers:
            patient_handover.status = form.cleaned_data['handover_status']
            patient_handover.save()
        
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


class AEConsultationFinishView(ClinicListView):
    template_name = 'ehr/doctor/ae_patient_seen.html'
    status_filter = 'seen'
    clinic_filter = 'A & E'
    room_filter = None


class AEAwaitingReviewView(ClinicListView):
    template_name = 'ehr/doctor/ae_review_patient.html'
    status_filter = 'review'
    clinic_filter = 'A & E'
    room_filter = None


class SOPDConsultationFinishView(ClinicListView):
    template_name = 'ehr/doctor/sopd_patient_seen.html'
    status_filter = 'seen'
    clinic_filter = 'SOPD'
    room_filter = None

class SOPDAwaitingReviewView(ClinicListView):
    template_name = 'ehr/doctor/sopd_review_patient.html'
    status_filter = 'review'
    clinic_filter = 'SOPD'
    room_filter = None
    

class AppointmentCreateView(RecordRequiredMixin, CreateView):
        model = Appointment
        form_class = AppointmentForm
        template_name = 'ehr/record/new_appointment.html'

        def form_valid(self, form):
            form.instance.user = self.request.user
            form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
            self.object = form.save()
            return super().form_valid(form)
        
        def get_success_url(self):
            messages.success(self.request, 'APPOINTMENT ADDED')
            return self.object.patient.get_absolute_url()


class AppointmentUpdateView(UpdateView):
    model = Appointment
    template_name = 'ehr/record/update_appt.html'
    form_class = AppointmentForm
    success_url = reverse_lazy("medical_record")

    
    def form_valid(self, form):
        messages.success(self.request, 'Appointment Updated Successfully')
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating appointment information')
        return self.render_to_response(self.get_context_data(form=form))


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


class ServiceCreateView(RevenueRequiredMixin, CreateView):
        model = Services
        form_class = ServiceForm
        template_name = 'ehr/revenue/new_service.html'
        success_url = reverse_lazy("service_list")

        def form_valid(self, form):
            messages.success(self.request, 'SERVICE ADDED')
            return super().form_valid(form)

 
class ServiceUpdateView(UpdateView):
    model = Services
    template_name = 'ehr/revenue/update_service.html'
    form_class = ServiceForm
    success_url = reverse_lazy("service_list")

    def form_valid(self, form):
        messages.success(self.request, 'Service Updated Successfully')
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating appointment information')
        return self.render_to_response(self.get_context_data(form=form))


class ServiceListView(ListView):
    model=Services
    template_name='ehr/revenue/service_list.html'
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
            messages.success(self.request, 'PAYMENT ADDED')
            return super().form_valid(form)

 
class PayUpdateView(UpdateView):
    model = Paypoint
    template_name = 'ehr/revenue/update_pay.html'
    form_class = PayUpdateForm
    success_url = reverse_lazy("pay_list")

    def form_valid(self, form):
        paypoint = form.save()
        hematology_result = paypoint.hematology_result
        # Update hematology_result instance if needed
        messages.success(self.request, 'Payment Updated Successfully')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating appointment information')
        return self.render_to_response(self.get_context_data(form=form))


class PayListView(ListView):
    model=Paypoint
    template_name='ehr/revenue/pay_list.html'
    context_object_name='pays'
    paginate_by = 5

    def get_queryset(self):
        updated = super().get_queryset().filter(status='paid').order_by('-updated')
        pay_filter = PayFilter(self.request.GET, queryset=updated)
        return pay_filter.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()
        service_price_total = self.get_queryset().values('service__price').annotate(total=Sum('service__price')).aggregate(total_worth=Sum('total'))['total_worth'] or 0
        price_total = self.get_queryset().aggregate(total_worth=Sum('price'))['total_worth'] or 0
        total_worth = service_price_total + price_total

        context['payFilter'] = PayFilter(self.request.GET, queryset=self.get_queryset())
        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        return context    
    
class HematologyPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/hema_pay_list.html'
    context_object_name = 'hematology_pays'
    paginate_by = 5

    def get_queryset(self):
        return Paypoint.objects.filter(hematology_result__isnull=False).order_by('-updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

         # Calculate total worth only for paid transactions
        paid_transactions = self.get_queryset().filter(status='paid')
        service_price_total = paid_transactions.values('service__price').annotate(total=Sum('service__price')).aggregate(total_worth=Sum('total'))['total_worth'] or 0
        price_total = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0
        total_worth = service_price_total + price_total

        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        return context  
