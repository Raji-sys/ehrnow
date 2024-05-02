from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from .models import *
from .forms import *
from .filters import *
from django.contrib.auth import get_user_model
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime
from django.conf import settings
import os
import csv
from django.db.models import Count
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, FormView, ListView, DetailView, UpdateView
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
        if self.request.user.is_superuser:
            pass
        else:
            return reverse_lazy('login')


# @method_decorator(login_required(login_url='login'), name='dispatch')
# class UpdateUserView(UpdateView):
#     model = User
#     template_name = 'patient/update-user.html'
#     form_class = UserForm
#     success_url = reverse_lazy('profile_folder')

#     def get_success_url(self):
#         messages.success(
#             self.request, 'patient Information Updated Successfully')
#         return reverse_lazy('profile_folder', kwargs={'username': self.object.username})

#     def form_valid(self, form):
#         if form.is_valid():
#             form.save()
#             return super().form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, 'error updating patient information')
#         return self.render_to_response(self.get_context_data(form=form))

class IndexView(TemplateView):
    template_name = "index.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class GetStartedView(TemplateView):
    template_name = "get_started.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class MedicalRecordView(TemplateView):
    template_name = "ehr/dashboard/medical_record.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class RevenueView(TemplateView):
    template_name = "ehr/dashboard/revenue.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class NursingView(TemplateView):
    template_name = "ehr/dashboard/nursing.html"


@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicView(TemplateView):
    template_name = "ehr/dashboard/clinic.html"


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
        return self.request.user.groups.filter(name='Record').exists()

class RevenueRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Revenue').exists()

class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Doctor').exists()


# Views for Record officer
class PatientVisitView(RecordRequiredMixin, CreateView):
    model = PatientData
    form_class = PatientForm
    template_name = 'ehr/record/new_patient.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        file_no = self.request.GET.get('file_no')
        if file_no:
            try:
                patient = PatientData.objects.get(file_no=file_no)
                kwargs['instance'] = patient
            except PatientData.DoesNotExist:
                pass
        return kwargs

    def form_valid(self, form):
        patient = form.save()
        visit = Visit(patient=patient)
        visit.save()
        handover = PatientHandover(patient=patient, status='waiting_for_payment')
        handover.save()

        if 'file_no' in self.request.GET:
            messages.success(self.request, 'Patient visit created successfully. Please hand over to the paypoint.')
        else:
            messages.success(self.request, 'New patient created successfully. Please hand over to the paypoint.')

        return redirect('record_dash')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_no = self.request.GET.get('file_no')
        if file_no:
            try:
                patient = PatientData.objects.get(file_no=file_no)
                context['is_new_visit'] = True
            except PatientData.DoesNotExist:
                context['is_new_visit'] = False
        else:
            context['is_new_visit'] = False
        return context

@method_decorator(login_required(login_url='login'), name='dispatch')
class PatientFolderView(DetailView):
    template_name = 'ehr/patient/patient_folder.html'
    model = PatientData

    def get_object(self, queryset=None):
        if self.request.user.is_superuser or self.request.user.is_staff:
            file_number = self.kwargs.get('file_no')
            return get_object_or_404(PatientData, file_no=file_number)
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = context['object']

        vitals = VitalSigns.objects.filter(patient=patient.file_no)

        context['vitals'] = vitals
        context['VitalSignsform'] = VitalSignsForm()
        return context
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class UpdatePatientView(UpdateView):
    model = PatientData
    template_name = 'ehr/record/patient/update-profile.html'
    form_class = PatientForm
    success_url = reverse_lazy('patient_folder')

    def get_success_url(self):
        file_number = self.object.file_no
        messages.success(
            self.request, 'Patient Information Updated Successfully'
        )
        return reverse_lazy('patient_folder', kwargs={'file_no': file_number})

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating patient information')
        return self.render_to_response(self.get_context_data(form=form))
    

class RecordDashboardView(RecordRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/record/record_dash.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status__in=['waiting_for_clinic_assignment', 'waiting_for_vital_signs'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class AssignClinicView(RecordRequiredMixin, UpdateView):
    model = PatientHandover
    fields = ['clinic']
    template_name = 'ehr/record/assign_clinic.html'

    def form_valid(self, form):
        handover = form.save(commit=False)
        handover.status = 'waiting_for_vital_signs'
        handover.save()
        messages.success(self.request, 'Patient assigned to the clinic successfully.')
        return redirect('record_dash')


# class HandleVisitView(RecordRequiredMixin, CreateView):
#     model = Visit
#     form_class = VisitForm
#     template_name = 'ehr/record/handle_visit.html'

#     def form_valid(self, form):
#         visit = form.save(commit=False)
#         patient = visit.patient
#         clinic = visit.clinic

#         handover = PatientHandover.objects.create(
#             patient=patient,
#             clinic=clinic,
#             status='waiting_for_payment'
#         )

#         messages.success(self.request, 'Patient handed over for payment.')
#         return redirect('record_dashboard')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['is_new_visit'] = True
#         return context

# Views for Payment Clerk
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

        # Process payment
        payment = Paypoint.objects.create(patient=patient, status='paid')

        # Update the PatientHandover status to 'waiting_for_vital_signs'
        handover.status = 'waiting_for_vital_signs'
        handover.save()

        messages.success(self.request, 'Payment successful. Patient handed over for vital signs.')
        return redirect('paypoint_dash')


class PaypointDashboardView(RevenueRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/revenue/paypoint_dash.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='waiting_for_payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class NursingDeskView(LoginRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/nurse/nursing_desk.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='waiting_for_vital_signs')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class VitalSignCreateView(CreateView):
    model = VitalSigns
    form_class = VitalSignsForm
    template_name = 'staff/qual.html'

    def form_valid(self, form):
        if self.request.user.is_superuser:
            # If the current user is a superuser, use the username from the URL
            username_from_url = self.kwargs.get('username')
            user = get_object_or_404(User, username=username_from_url)
            form.instance.user = user
        else:
            # If the current user is not a superuser, use the current user
            form.instance.user = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Vital Signs Added Successfully')
        return reverse_lazy('patient_folder', kwargs={'username': self.kwargs['username']})


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
class VitalsDeleteView(DeleteView):
    model = VitalSigns
    template_name = 'staff/qual-delete-confirm.html'

    def get_success_url(self):
        file_number = self.object.file_no
        messages.success(
            self.request, 'Patient Information Updated Successfully'
        )
        return reverse_lazy('patient_folder', kwargs={'file_no': file_number})

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 302:
            messages.success(
                self.request, 'VitalSigns deleted successfully')
        else:
            messages.error(self.request, 'Error deleting VitalSigns')
        return response


class ConsultationRoomView(DoctorRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'ehr/doctor/doctors_list.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='waiting_for_consultation') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    