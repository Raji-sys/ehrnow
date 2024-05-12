# Original views
class AEConsultationWaitRoomView(DoctorRequiredMixin, ListView):
    ...

# Replaced by
class AEConsultationWaitRoomView(ClinicListView):
    template_name = 'ehr/clinic/ae_list.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "A & E"
    room_filter = None

# Original views  
class AERoom1View(DoctorRequiredMixin, ListView):
    ...

# Replaced by
class AERoom1View(ClinicListView):
    template_name = 'ehr/clinic/ae_room1.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "A & E"
    room_filter = 'ROOM 1'

# Original views
class AERoom2View(DoctorRequiredMixin, ListView):
    ...

# Replaced by (assuming you need this view)
class AERoom2View(ClinicListView):
    template_name = 'ehr/clinic/ae_room2.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "A & E"
    room_filter = 'ROOM 2'

# Original views
class SOPDConsultationWaitRoomView(DoctorRequiredMixin, ListView):
    ...

# Replaced by
class SOPDConsultationWaitRoomView(ClinicListView):
    template_name = 'ehr/clinic/sopd_list.html'
    status_filter = 'waiting_for_consultation'
    clinic_filter = "SOPD"
    room_filter = None

# Original views
class AEConsultationFinishView(ListView):
    ...

# Replaced by
class AEConsultationFinishView(ClinicListView):
    template_name = 'ehr/doctor/patient_seen.html'
    status_filter = 'seen_by_doctor'
    clinic_filter = 'A & E'
    room_filter = None

# Original views
class AEAwaitingReviewView(ListView):
    ...

# Replaced by
class AEAwaitingReviewView(ClinicListView):
    template_name = 'ehr/doctor/review_patient.html'
    status_filter = 'awaiting_review'
    clinic_filter = 'A & E'
    room_filter = None

# Original views
class SOPDConsultationFinishView(ListView):
    ...

# Replaced by
class SOPDConsultationFinishView(ClinicListView):
    template_name = 'ehr/doctor/patient_seen.html'
    status_filter = 'seen_by_doctor'
    clinic_filter = 'SOPD'
    room_filter = None

# Original views
class SOPDAwaitingReviewView(ListView):
    ...

# Replaced by
class SOPDAwaitingReviewView(ClinicListView):
    template_name = 'ehr/doctor/review_patient.html'
    status_filter = 'awaiting_review'
    clinic_filter = 'SOPD'
    room_filter = None




class PaypointView(RevenueRequiredMixin, FormView):
    template_name = 'ehr/revenue/paypoint.html'
    form_class = PaypointForm
    success_url = reverse_lazy("revenue")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        handover_id = self.kwargs.get('handover_id')
        handover = get_object_or_404(PatientHandover, id=handover_id)
        context['patient'] = handover.patient
        context['handover'] = handover
        service_name= 'new registration'
        service=Services.objects.get(name=service_name)
        context['service_name']=service.name
        context['service_price']=service.price
        return context

    def form_valid(self, form):
        handover_id = self.kwargs.get('handover_id')
        handover = get_object_or_404(PatientHandover, id=handover_id)
        patient = handover.patient
        new_registration_service = Services.objects.get(name='new registration')
        payment = Paypoint.objects.create(patient=patient,status='paid',service=new_registration_service)
        handover.status = 'waiting_for_vital_signs'
        handover.save()
        messages.success(self.request, 'Payment successful. Patient handed over for vital signs.')
        return super().form_valid(form)


class PaypointFollowUpView(RevenueRequiredMixin, FormView):
    template_name = 'ehr/revenue/paypoint_follow_up.html'
    form_class = PaypointForm
    success_url = reverse_lazy("revenue")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        handover_id = self.kwargs.get('handover_id')
        handover = get_object_or_404(PatientHandover, id=handover_id)
        context['patient'] = handover.patient
        context['handover'] = handover
        service_name= 'follow up'
        service=Services.objects.get(name=service_name)
        context['service_name']=service.name
        context['service_price']=service.price
        return context

    def form_valid(self, form):
        handover_id = self.kwargs.get('handover_id')
        handover = get_object_or_404(PatientHandover, id=handover_id)
        patient = handover.patient

        follow_up_service = Services.objects.get(name='follow up')
        payment = Paypoint.objects.create(
            patient=patient,
            status='paid',
            service=follow_up_service
        )

        handover.status = 'waiting_for_vital_signs'
        handover.save()

        messages.success(self.request, 'Payment successful. Patient handed over for follow-up consultation.')
        return super().form_valid(form)
