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
from django.db.models import Prefetch
User = get_user_model()


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
            pass
            # return reverse_lazy('profile_folder', args=[self.request.user.username])


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
    template_name = "index.html"


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
    template_name = "ehr/dashboard/clinics_dash.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicView(TemplateView):
    template_name = "ehr/record/clinic.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class WaitRoomView(TemplateView):
    template_name = "ehr/record/wait_room.html"


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

# Mixins
class RecordRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='record').exists()

class RevenueRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='revenue').exists()

class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='doctor').exists()

#1 Patient create
class PatientCreateView(RecordRequiredMixin, CreateView):
    model = PatientData
    form_class = PatientForm
    template_name = 'ehr/record/new_patient.html'
    success_url = reverse_lazy("record_dash")

    def form_valid(self, form):
        patient = form.save()
        clinic = form.cleaned_data['clinic']
        team = form.cleaned_data.get('team', clinic)  # Assuming team is optional and defaults to clinic
        PatientHandover.objects.create(patient=patient, clinic=clinic, team=team, status='waiting_for_payment')
        messages.success(self.request, 'Patient created successfully')
        return super().form_valid(form)

# 2. FollowUpVisitCreateView
class FollowUpVisitCreateView(RecordRequiredMixin, CreateView):
    model = FollowUpVisit
    form_class = VisitForm
    template_name = 'ehr/record/follow_up.html'
    success_url = reverse_lazy("record_dash")

    def get_object(self, queryset=None):
        patient_id = self.kwargs.get('pk')
        return PatientData.objects.get(id=patient_id)

    def form_valid(self, form):
        patient = self.get_object()
        visit = form.save(commit=False)
        visit.patient = patient
        visit.save()

        clinic = form.cleaned_data['clinic']
        team = form.cleaned_data.get('team', clinic)  # Assuming team is optional and defaults to clinic
        PatientHandover.objects.update_or_create(
            patient=patient,
            defaults={
                'clinic': clinic,
                'team': team,
                'status': 'waiting_for_payment'
            }
        )

        messages.success(self.request, 'Follow-up visit created successfully')
        return redirect(self.success_url)


# 3. RecordDashboardView
class RecordDashboardView(RecordRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/record/record_dash.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status__in=['waiting_for_payment'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# 4. PaypointView
class PaypointView(RevenueRequiredMixin, FormView):
    template_name = 'ehr/revenue/paypoint.html'
    form_class = PaypointForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        handover_id = self.kwargs.get('handover_id')
        handover = get_object_or_404(PatientHandover, id=handover_id)
        context['patient'] = handover.patient
        context['handover'] = handover
        return context

    def form_valid(self, form):
        handover_id = self.kwargs.get('handover_id')
        handover = get_object_or_404(PatientHandover, id=handover_id)
        patient = handover.patient

        new_registration_service = Services.objects.get(name='new registration')

        # Process payment
        payment = Paypoint.objects.create(
            patient=patient,
            status='paid',
            service=new_registration_service
        )

        # Update the PatientHandover status to 'waiting_for_vital_signs'
        handover.status = 'waiting_for_vital_signs'
        handover.save()

        messages.success(self.request, 'Payment successful. Patient handed over for vital signs.')
        return redirect('paypoint_dash')

# 5. PaypointDashboardView
class PaypointDashboardView(RevenueRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/revenue/paypoint_dash.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='waiting_for_payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# 6. NursingDeskView
class NursingDeskView(LoginRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/nurse/nursing_desk.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='waiting_for_vital_signs')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# 7. ClinicListView (Abstract Base Class)
class ClinicListView(ListView):
    model = PatientData
    template_name = 'ehr/record/clinic_list.html'
    context_object_name = 'patients'

    def get_queryset(self):
        clinic_name = self.kwargs.get('clinic_name')
        clinic = Clinic.objects.get(name=clinic_name)
        return self.filter_queryset(clinic)

    def filter_queryset(self, clinic):
        raise NotImplementedError("Subclasses should implement this method.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic_name'] = self.kwargs.get('clinic_name')
        return context
    

# 8. PatientsByClinicListView (Subclass of ClinicListView)
class PatientsByClinicListView(ClinicListView):
    def filter_queryset(self, clinic):
        return PatientData.objects.filter(handovers__clinic=clinic, handovers__status='waiting_for_consultation')    
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
        return context
    
# 9. FollowUpPatientsByClinicListView (Subclass of ClinicListView)
class FollowUpPatientsByClinicListView(ClinicListView):
    def filter_queryset(self, clinic):
        return PatientData.objects.filter(
            followupvisit__isnull=False,
            handovers__clinic=clinic,
            handovers__status='waiting_for_consultation'
        ).distinct()
@method_decorator(login_required(login_url='login'), name='dispatch')

#10 Room View
class RoomView(TemplateView):
    template_name = 'ehr/record/room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = kwargs.get('room_id')
        room = Room.objects.get(id=room_id)
        context['room'] = room
        return context

#11 Clinic Base
class ClinicBaseView(TemplateView):
    template_name = 'ehr/record/room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic_name = self.get_clinic_name()
        rooms = Room.objects.filter(clinic__name=clinic_name).prefetch_related(
            Prefetch('patients', queryset=PatientData.objects.filter(
                handovers__clinic__name=clinic_name,
                handovers__status__in=['waiting_for_consultation', 'seen_by_doctor', 'awaiting_review']
            ).annotate(
                waiting_room_count=models.Count('waitingroom')
            ).filter(waitingroom__count__gt=0))
        )
        context['clinic_name'] = clinic_name
        context['rooms'] = rooms
        return context

    def get_clinic_name(self):
        raise NotImplementedError("Subclasses should implement this method.")

#11 AE clinic        
class AEClinicView(ClinicBaseView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic_name'] = 'A & E'
        rooms = Room.objects.filter(clinic__name='A & E').prefetch_related(
            Prefetch('patients', queryset=PatientData.objects.annotate(
                waiting_room_count=models.Count('waitingroom')
            ).filter(waitingroom__count__gt=0))
        )        
        context['rooms'] = rooms        
        return context

#12 GOPD clinic        
class GOPDClinicView(ClinicBaseView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic_name'] = 'GOPD'
        rooms = Room.objects.filter(clinic__name='GOPD').prefetch_related(
            Prefetch('patients', queryset=PatientData.objects.annotate(
                waiting_room_count=models.Count('waitingroom')
            ).filter(waitingroom__count__gt=0))
        )
        context['rooms'] = rooms       
        return context

#13 SOPD clinic        
class SOPDClinicView(ClinicBaseView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic_name'] = 'SOPD'
        rooms = Room.objects.filter(clinic__name='SOPD').prefetch_related(
            Prefetch('patients', queryset=PatientData.objects.annotate(
                waiting_room_count=models.Count('waitingroom')
            ).filter(waitingroom__count__gt=0))
        )
        context['rooms'] = rooms               
        return context
    
#14 Assign clinic        
class AssignClinicView(RecordRequiredMixin, UpdateView):
    model = PatientHandover
    fields = ['clinic']
    template_name = 'ehr/record/assign_clinic.html'

    def form_valid(self, form):
        handover = form.save(commit=False)
        handover.status = 'waiting_for_consultation'
        handover.save()
        messages.success(self.request, 'Patient assigned to the clinic successfully.')
        return redirect('record_dash')

#15
class ConsultationWaitRoomView(DoctorRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/doctor/doctors_list.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status__in=['waiting_for_consultation', 'seen_by_doctor'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PatientAwaitingReviewListView(DoctorRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/doctor/patients_awaiting_review.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='awaiting_review')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context 

class PatientAwaitingReviewView(DoctorRequiredMixin, UpdateView):
    model = PatientHandover
    fields = []
    template_name = 'ehr/doctor/patient_awaiting_review.html'
    success_url = reverse_lazy('doctor_consultation_list')

    def get_object(self, queryset=None):
        handover_id = self.kwargs.get('handover_id')
        return get_object_or_404(PatientHandover, id=handover_id)

    def form_valid(self, form):
        handover = form.instance
        handover.status = 'awaiting_review'
        handover.save()
        messages.success(self.request, 'Patient awaiting review.')
        return redirect(self.success_url)   


class PatientSeenByDoctorView(DoctorRequiredMixin, UpdateView):
    model = PatientHandover
    fields = []
    template_name = 'ehr/doctor/patient_seen.html'
    success_url = reverse_lazy('doctor_consultation_list')

    def get_object(self, queryset=None):
        handover_id = self.kwargs.get('handover_id')
        return get_object_or_404(PatientHandover, id=handover_id)

    def form_valid(self, form):
        handover = form.instance
        handover.status = 'seen_by_doctor'
        handover.save()
        messages.success(self.request, 'Patient seen by doctor.')
        return redirect(self.success_url)
    
    
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
    

    
@method_decorator(login_required(login_url='login'), name='dispatch')
class PatientMovementView(ListView):
    model = PatientHandover
    template_name = "ehr/record/patient_moves.html"

    def get_queryset(self):
        status_values = ('waiting_for_payment', 'waiting_for_vital_signs', 'waiting_for_clinic_assignment', 'waiting_for_consultation')
        return PatientHandover.objects.filter(status__in=status_values)


@method_decorator(login_required(login_url='login'), name='dispatch')
class VitalSignCreateView(CreateView):
    model = VitalSigns
    form_class = VitalSignsForm
    template_name = 'ehr/nurse/vital_signs.html'


    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        self.object = form.save()

        # Update the related PatientHandover object
        patient_handover = PatientHandover.objects.filter(patient=form.instance.patient).first()
        if patient_handover:
            patient_handover.handover_status = 'waiting_for_consultation'
            patient_handover.status = 'waiting_for_consultation'  # Update the status field
            patient_handover.save()

        return super().form_valid(form)

    def test_func(self):
        allowed_groups = ['nurse']
        return any(group in self.request.user.groups.values_list('name', flat=True) for group in allowed_groups)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = PatientData.objects.get(file_no=self.kwargs['file_no'])
        return context

    def get_success_url(self):
        messages.success(self.request, 'Vitals taken, Patient handed over for consultation.')
        return reverse_lazy('nursing_station')
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class VitalsUpdateView(UpdateView):
    model = VitalSigns
    form_class = VitalSignsForm
    template_name = 'staff/qual-update.html'

    def get_success_url(self):
        file_number = self.object.file_no
        messages.success(
            self.request, 'Patient Information Updated Successfully'
        )
        return reverse_lazy('patient_folder', kwargs={'file_no': file_number})
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error Updating VitalSigns')
        return super().form_invalid(form)


@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicalNoteCreateView(CreateView, DoctorRequiredMixin):
    model = ClinicalNote
    form_class = ClinicalNoteForm
    template_name = 'ehr/doctor/clinical_note.html'


    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        self.object = form.save()

        # Update the related PatientHandover object
        patient_handover = PatientHandover.objects.filter(patient=form.instance.patient).first()
        if patient_handover:
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
        return reverse_lazy('clinic')


class ConsultationFinishView(ListView):
    model = PatientHandover
    template_name = 'ehr/doctor/patient_seen.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='seen_by_doctor') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class AwaitingReviewView(ListView):
    model = PatientHandover
    template_name = 'ehr/doctor/review_patient.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='awaiting_review') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
