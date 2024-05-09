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
            ).filter(waiting_room_count__gt=0))
        )
        context['clinic_name'] = clinic_name
        context['rooms'] = rooms
        return context

    def get_clinic_name(self):
        raise NotImplementedError("Subclasses should implement this method.")


class AEClinicView(ClinicBaseView):
    def get_clinic_name(self):
        return 'A & E'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clinic_name'] = 'A & E'
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


"""QUESTIONAABLE VIEWS"""
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
