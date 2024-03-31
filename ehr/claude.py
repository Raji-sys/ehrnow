# models.py
from django.db import models

class Patient(models.Model):
    # Patient model fields

class Payment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Clinic(models.Model):
    # Clinic model fields

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='scheduled')

class PatientHandover(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='handovers')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, blank=True, related_name='handovers')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True, related_name='handovers')
    status = models.CharField(max_length=30, choices=[
        ('waiting_for_payment', 'Waiting for Payment'),
        ('waiting_for_clinic_assignment', 'Waiting for Clinic Assignment'),
        ('waiting_for_vital_signs', 'Waiting for Vital Signs'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# forms.py
from django import forms
from .models import Patient, Appointment

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'contact_details']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['clinic', 'appointment_date', 'reason']

# views.py
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, FormView, ListView, DetailView, UpdateView
from .models import Patient, PatientHandover, Payment, Appointment
from .forms import PatientForm, AppointmentForm

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
    model = Patient
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

class HandleAppointmentView(ReceptionistRequiredMixin, DetailView):
    model = Appointment
    template_name = 'handle_appointment.html'
    context_object_name = 'appointment'

    def post(self, request, *args, **kwargs):
        appointment = self.get_object()
        handover = PatientHandover.objects.create(
            patient=appointment.patient,
            clinic=appointment.clinic,
            appointment=appointment,
            status='waiting_for_payment'
        )
        messages.success(request, 'Patient handed over for payment.')
        return redirect('receptionist_dashboard')

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
        payment = Payment.objects.create(patient=patient, status='paid')

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

# Views for Doctor
class ScheduleAppointmentView(DoctorRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'schedule_appointment.html'

    def form_valid(self, form):
        patient_id = self.kwargs.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)
        appointment = form.save(commit=False)
        appointment.patient = patient
        appointment.save()
        messages.success(self.request, 'Appointment scheduled successfully.')
        return redirect('doctor_dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)
        context['patient'] = patient
        return context

# Other views (NursingDesk, ConsultationRoom, etc.) can be implemented similarly

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Receptionist URLs
    path('create-patient/', views.CreatePatientView.as_view(), name='create_patient'),
    path('receptionist-dashboard/', views.ReceptionistDashboardView.as_view(), name='receptionist_dashboard'),
    path('handle-appointment/<int:pk>/', views.HandleAppointmentView.as_view(), name='handle_appointment'),
    path('assign-clinic/<int:pk>/', views.AssignClinicView.as_view(), name='assign_clinic'),

    # Payment Clerk URLs
    path('payment/<int:handover_id>/', views.PaymentView.as_view(), name='payment'),
    path('payment-clerk-dashboard/', views.PaymentClerkDashboardView.as_view(), name='payment_clerk_dashboard'),

    # Doctor URLs
    path('schedule-appointment/<int:patient_id>/', views.ScheduleAppointmentView.as_view(), name='schedule_appointment'),

    # Other URLs for NursingDesk, ConsultationRoom, etc.
]