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
        return PatientHandover.objects.filter(
            status__in=['waiting_for_payment'],
            # clinic='Follow Up'  # Or any other clinic for follow-up visits
        )


class PaypointView(RevenueRequiredMixin, FormView):
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
            handover.status = 'waiting_for_vital_signs'
            handover.save()
            messages.success(self.request, 'Payment successful. Patient handed over for vital signs.')
        else:
            # Handle the case where no handover object is found
            pass

        return super().form_valid(form)


class PaypointFollowUpView(RevenueRequiredMixin, FormView):
    template_name = 'ehr/revenue/paypoint_follow_up.html'
    form_class = PaypointForm
    success_url = reverse_lazy("revenue")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        handover = patient.handovers.filter(status='waiting_for_payment').first()

        if handover:
            context['patient'] = patient
            context['handover'] = handover
            service_name = 'follow up'
            service = Services.objects.get(name=service_name)
            context['service_name'] = service.name
            context['service_price'] = service.price
        return context

    def form_valid(self, form):
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        handover = patient.handovers.filter(status='waiting_for_payment').first()

        if handover:
            follow_up_service = Services.objects.get(name='follow up')
            payment = Paypoint.objects.create(patient=patient, status='paid', service=follow_up_service)
            handover.status = 'waiting_for_vital_signs'
            handover.save()
            messages.success(self.request, 'Payment successful. Patient handed over for vitals.')
        else:
            # Handle the case where no handover object is found
            pass

        return super().form_valid(form)