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



# <!-- ehr/nurse/nursing_desk.html -->
# {% extends 'base.html' %}

# {% block content %}
#   <h2>Patient Handovers</h2>

#   <form>
#     <label for="clinic">Filter by Clinic:</label>
#     <select id="clinic" name="clinic">
#       <option value="">All Clinics</option>
#       {% for clinic in clinics %}
#         <option value="{{ clinic.pk }}">{{ clinic.name }}</option>
#       {% endfor %}
#     </select>

#     <label for="room">Filter by Room:</label>
#     <select id="room" name="room">
#       <option value="">All Rooms</option>
#       {% for room in rooms %}
#         <option value="{{ room.pk }}">{{ room.name }}</option>
#       {% endfor %}
#     </select>

#     <label for="status">Filter by Status:</label>
#     <select id="status" name="status">
#       <option value="">All Statuses</option>
#       <option value="waiting_for_vital_signs">Waiting for Vital Signs</option>
#       <option value="waiting_for_consultation">Waiting for Consultation</option>
#       <option value="awaiting_review">Awaiting Review</option>
#       <!-- Add more options for other statuses -->
#     </select>

#     <button type="submit">Filter</button>
#   </form>

#   {% if handovers %}
#     <table>
#       <thead>
#         <tr>
#           <th>Patient</th>
#           <th>Clinic</th>
#           <th>Room</th>
#           <th>Status</th>
#           <th>Actions</th>
#         </tr>
#       </thead>
#       <tbody>
#         {% for handover in handovers %}
#           <tr>
#             <td>{{ handover.patient }}</td>
#             <td>{{ handover.clinic.name }}</td>
#             <td>{{ handover.room.name }}</td>
#             <td>{{ handover.status }}</td>
#             <td>
#               {% if handover.status == 'waiting_for_vital_signs' %}
#                 <a href="{% url 'vital_signs' handover.patient.file_no %}">Take Vital Signs</a>
#               {% elif handover.status == 'waiting_for_consultation' %}
#                 <a href="{% url 'consultation' handover.patient.file_no %}">Start Consultation</a>
#               {% elif handover.status == 'awaiting_review' %}
#                 <a href="{% url 'review' handover.patient.file_no %}">Review Patient</a>
#               {% endif %}
#             </td>
#           </tr>
#         {% endfor %}
#       </tbody>
#     </table>
#   {% else %}
#     <p>No patients found.</p>
#   {% endif %}
# {% endblock %}


# {% extends 'base.html' %}
# {% load static %}

# {% block title %}WAITING FOR CONSULTATION{% endblock %}

# {% block page_title %}<div class="enom flex justify-center">WAITING FOR CONSULTATION</div>{% endblock %}

# {% block content %}

# <div class="mt-5 p-4">
#     <section class="max-w-xl mx-auto text-center border-cyan-700 p-4 m-2">
#         {% for message in messages %}
#         <div class="">
#             <div class="bg-green-100 rounded-2xl text-sm p-4" uk-alert>
#                 <a href class="uk-alert-close font-bold" uk-close></a>
#                 <p class="text-green-700 font-semibold">{{ message }}</p>
#             </div>
#         </div>
#         {% endfor %}
#     </section>

#     <div class="max-w-6xl mx-auto rounded-xl p-4 shadow-black shadow-2xl bg-emerald-50">
#         <div class="overflow-x-auto">
#             {% for clinic, room_groups in grouped_patients.items %}
#             <h2 class="text-lg font-bold mb-4">Clinic: {{ clinic }}</h2>
#             {% for room, patients in room_groups.items %}
#             <h3 class="text-md font-semibold mb-2">Room: {{ room }}</h3>
#             <table class="min-w-full divide-y divide-emerald-500">
#                 <thead class="bg-emerald-100">
#                     <tr>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">S/N</th>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">FILE NUMBER</th>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">PATIENT NAME</th>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">PHONE NUMBER</th>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">PROCESS</th>
#                     </tr>
#                 </thead>
#                 <tbody class="bg-white divide-y divide-emerald-200">
#                     {% for patient in patients %}
#                     <tr class="bg-emerald-50 hover:bg-emerald-200 transition-colors duration-300">
#                         <td class="px-6 py-4 whitespace-nowrap">{{ forloop.counter }}</td>
#                         <td class="px-6 py-4 whitespace-nowrap">{{ patient.file_no|default_if_none:'' }}</td>
#                         <td class="px-6 py-4 whitespace-nowrap">{{ patient.full_name|default_if_none:'' }}</td>
#                         <td class="px-6 py-4 whitespace-nowrap">{{ patient.phone|default_if_none:'' }}</td>
#                         <td class="px-6 py-4 whitespace-nowrap">
#                             <a href="{{ patient.get_absolute_url }}">process</a>
#                         </td>
#                     </tr>
#                     {% endfor %}
#                 </tbody>
#             </table>
#             {% endfor %}
#             {% endfor %}
#         </div>
#     </div>
# </div>

# {% endblock %}

# {% extends 'base.html' %}
# {% load static %}

# {% block title %}NURSING DESK{% endblock %}

# {% block page_title %}<div class="enom flex justify-center">NURSING DESK</div>{% endblock %}

# {% block content %}
# <div class="mt-5 p-4">
#     <section class="max-w-xl mx-auto text-center border-cyan-700 p-4 m-2">
#         {% for message in messages %}
#         <div class="">
#             <div class="bg-green-100 rounded-2xl text-sm p-4" uk-alert>
#                 <a href class="uk-alert-close font-bold" uk-close></a>
#                 <p class="text-green-700 font-semibold">{{ message }}</p>
#             </div>
#         </div>
#         {% endfor %}
#     </section>

#     <div class="max-w-6xl mx-auto rounded-xl p-4 shadow-black shadow-2xl bg-emerald-50">
#         <div class="overflow-x-auto">
#             {% for clinic, room_groups in grouped_patients.items %}
#             <h2 class="text-lg font-bold mb-4">Clinic: {{ clinic }}</h2>
#             {% for room, patients in room_groups.items %}
#             <h3 class="text-md font-semibold mb-2">Room: {{ room }}</h3>
#             <table class="min-w-full divide-y divide-emerald-500">
#                 <thead class="bg-emerald-100">
#                     <tr>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">S/N</th>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">FILE NUMBER</th>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">PATIENT NAME</th>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">PHONE NUMBER</th>
#                         <th class="px-6 py-3 text-left text-xs font-medium text-emerald-500 uppercase tracking-wider">PROCESS</th>
#                     </tr>
#                 </thead>
#                 <tbody class="bg-white divide-y divide-emerald-200">
#                     {% for patient in patients %}
#                     <tr class="bg-emerald-50 hover:bg-emerald-200 transition-colors duration-300">
#                         <td class="px-6 py-4 whitespace-nowrap">{{ forloop.counter }}</td>
#                         <td class="px-6 py-4 whitespace-nowrap">{{ patient.file_no|default_if_none:'' }}</td>
#                         <td class="px-6 py-4 whitespace-nowrap">{{ patient.full_name|default_if_none:'' }}</td>
#                         <td class="px-6 py-4 whitespace-nowrap">{{ patient.phone|default_if_none:'' }}</td>
#                         <td class="px-6 py-4 whitespace-nowrap">
#                             <a href="{{ patient.get_absolute_url }}">process</a>
#                         </td>
#                     </tr>
#                     {% endfor %}
#                 </tbody>
#             </table>
#             {% endfor %}
#             {% endfor %}
#         </div>
#     </div>
# </div>
# {% endblock %}