@method_decorator(login_required(login_url='login'), name='dispatch')
class ClinicalNoteCreateView(CreateView, DoctorRequiredMixin):
    model = ClinicalNote
    form_class = ClinicalNoteForm
    template_name = 'ehr/doctor/clinical_note.html'
    def form_valid(self, form):
        form.instance.user = self.request.user
        patient_data = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient_data
        self.object = form.save()

        # Update handover status to 'waiting_for_consultation'
        patient_handovers = PatientHandover.objects.filter(patient=patient_data)
        for patient_handover in patient_handovers:
            patient_handover.status = 'consultated'
            patient_handover.clinic = patient_handover.clinic
            patient_handover.room = form.cleaned_data['handover_room']
            patient_handover.save()

        # If there are no existing handovers, create a new one
        if not patient_handovers.exists():
            PatientHandover.objects.create(patient=patient_data, status='consultate')
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