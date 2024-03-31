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
            # return reverse_lazy('profile_details', args=[self.request.user.username])


@method_decorator(login_required(login_url='login'), name='dispatch')
class CustomLogoutView(LogoutView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, 'logout successful')
        return response


def reg_anonymous_required(view_function, redirect_to=None):
    if redirect_to is None:
        redirect_to = '/'
    return user_passes_test(lambda u: not u.is_authenticated or u.is_superuser, login_url=redirect_to)(view_function)


# @method_decorator(reg_anonymous_required, name='dispatch')
# class UserRegistrationView(CreateView):
#     form_class = CustomUserCreationForm
#     template_name = 'registration/register.html'
#     success_url = ""

#     def form_valid(self, form):
#         if form.is_valid():
#             response = super().form_valid(form)
#             user = User.objects.get(username=form.cleaned_data['username'])
#             profile_instance = Profile(user=user)
#             profile_instance.save()
#             # govapp_instance = GovernmentAppointment(user=user)
#             # govapp_instance.save()
#             messages.success(
#                 self.request, f"Registration for: {user.get_full_name()} was successful")
#             return response
#         else:
#             print("Form errors:", form.errors)
#             return self.form_invalid(form)

#     def get_success_url(self):
#         if self.request.user.is_superuser:
#             pass
#             # return reverse_lazy('patient')
#         else:
#             return reverse_lazy('index')


# @method_decorator(login_required(login_url='login'), name='dispatch')
# class UpdateUserView(UpdateView):
#     model = User
#     template_name = 'patient/update-user.html'
#     form_class = UserForm
#     success_url = reverse_lazy('profile_details')

#     def get_success_url(self):
#         messages.success(
#             self.request, 'patient Information Updated Successfully')
#         return reverse_lazy('profile_details', kwargs={'username': self.object.username})

#     def form_valid(self, form):
#         if form.is_valid():
#             form.save()
#             return super().form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, 'error updating patient information')
#         return self.render_to_response(self.get_context_data(form=form))


# @method_decorator(login_required(login_url='login'), name='dispatch')
# class UpdateProfileView(UpdateView):
#     model = Profile
#     template_name = 'patient/update-profile.html'
#     form_class = ProfileForm
#     success_url = reverse_lazy('profile_details')

#     def get_success_url(self):
#         messages.success(
#             self.request, 'patient Information Updated Successfully')
#         return reverse_lazy('profile_details', kwargs={'username': self.object.user})

#     def form_valid(self, form):
#         if form.is_valid():
#             form.save()
#             return super().form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, 'error updating patient information')
#         return self.render_to_response(self.get_context_data(form=form))


# @method_decorator(login_required(login_url='login'), name='dispatch')
# class ProfileDetailView(DetailView):
#     template_name = 'patient/profile_details.html'
#     model = Profile

#     def get_object(self, queryset=None):
#         if self.request.user.is_superuser:
#             username_from_url = self.kwargs.get('username')
#             user = get_object_or_404(User, username=username_from_url)
#         else:
#             user = self.request.user
#         return get_object_or_404(Profile, user=user)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         profile = context['object']

#         qualifications = Qualification.objects.filter(user=profile.user)

#         context['qualifications'] = qualifications
#         context['Qualform'] = QualForm()
#         return context

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
class ReceptionistRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Receptionist').exists()

class PaymentClerkRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='PaymentClerk').exists()

class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Doctor').exists()


# Views for Receptionist
class CreatePatientView(ReceptionistRequiredMixin, CreateView):
    model = PatientData
    form_class = PatientForm

    def form_valid(self, form):
        patient = form.save()
        handover = PatientHandover.objects.create(
            patient=patient,
            status='waiting_for_payment'
        )
        messages.success(self.request, 'Patient created successfully. Please hand over to the payment clerk.')
        return redirect('receptionist_dashboard')

class ReceptionistDashboardView(ReceptionistRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'receptionist_dashboard.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status__in=['waiting_for_clinic_assignment', 'waiting_for_vital_signs'])

class HandleAppointmentView(ReceptionistRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'handle_appointment.html'

    def form_valid(self, form):
        appointment = form.save(commit=False)
        patient = appointment.patient
        clinic = appointment.clinic

        handover = PatientHandover.objects.create(
            patient=patient,
            clinic=clinic,
            status='waiting_for_payment'
        )

        messages.success(self.request, 'Patient handed over for payment.')
        return redirect('receptionist_dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_new_appointment'] = True
        return context

class AssignClinicView(ReceptionistRequiredMixin, UpdateView):
    model = PatientHandover
    fields = ['clinic']
    template_name = 'assign_clinic.html'

    def form_valid(self, form):
        handover = form.save(commit=False)
        handover.status = 'waiting_for_vital_signs'
        handover.save()
        messages.success(self.request, 'Patient assigned to the clinic successfully.')
        return redirect('receptionist_dashboard')

# Views for Payment Clerk
class PaymentView(PaymentClerkRequiredMixin, FormView):
    template_name = 'payment.html'
    form_class = forms.Form  # Replace with your payment form if needed

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
        return redirect('payment_clerk_dashboard')


class PaymentClerkDashboardView(PaymentClerkRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'payment_clerk_dashboard.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='waiting_for_payment')


class NursingDeskView(LoginRequiredMixin, ListView):
    model = PatientHandover
    template_name = 'nursing_desk.html'
    context_object_name = 'handovers'

    def get_queryset(self):
        return PatientHandover.objects.filter(status='waiting_for_vital_signs')

class ConsultationRoomView(DoctorRequiredMixin, DetailView):
    model = PatientHandover
    template_name = 'consultation_room.html'
    context_object_name = 'handover'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        handover = self.get_object()
        context['patient'] = handover.patient
        return context