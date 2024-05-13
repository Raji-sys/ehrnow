class HematologyTestCreateView(LoginRequiredMixin, CreateView):
    model = HematologyResult
    form_class = HematologyTestForm
    template_name = 'hema/hematology_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hematology_service_type = Services.objects.get(name='hematology')
        context['available_tests'] = HematologyTest.objects.filter(service__type=hematology_service_type)
        return context

    def form_valid(self, form):
        patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        form.instance.patient = patient
        hematology_result = form.save()
        messages.success(self.request, 'Hematology result created successfully.')
        return super().form_valid(form)
#     def form_valid(self, form):
#         patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
#         form.instance.patient = patient
#         form.instance.collected_by = self.request.user
#         hematology_result = form.save()
 
# #        Get the hematology services for the patient
#         hematology_services = Services.objects.filter(type__name='Hematology')
#         if hematology_services.exists():
#             # Create a Paypoint instance for each hematology service
#             for service in hematology_services:
#                 Paypoint.objects.create(
#                     user=self.request.user,
#                     patient=hematology_result.patient,
#                     service=service,
#                     status='pending')
#         else:
#             messages.warning(self.request, 'No hematology services found.')            
#         messages.success(self.request, 'Hematology result -created successfully')
#         return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.patient.get_absolute_url()
    






class PaypointView(RevenueRequiredMixin, CreateView):
    model = Paypoint
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

            # Retrieve all pending services for the patient
            pending_paypoints = Paypoint.objects.filter(patient=patient, status='pending').prefetch_related(
                Prefetch('service', queryset=Services.objects.select_related('type'))
            )

            context['pending_services'] = []
            for paypoint in pending_paypoints:
                service_info = {
                    'name': paypoint.service.name,
                    'price': paypoint.service.price,
                    'department': paypoint.service.type.name,
                }
                context['pending_services'].append(service_info)

        else:
            # Handle the case where no handover object is found
            pass

        return context

    def form_valid(self, form):
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        paypoints = Paypoint.objects.filter(patient=patient, status='pending')

        for paypoint in paypoints:
            paypoint.status = 'paid'
            paypoint.save()

        messages.success(self.request, 'Payment successful.')
        return super().form_valid(form)  
# class PaypointView(RevenueRequiredMixin, CreateView):
#     model=Paypoint
#     template_name = 'ehr/revenue/paypoint.html'
#     form_class = PaypointForm
#     success_url = reverse_lazy("revenue")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         file_no = self.kwargs.get('file_no')
#         patient = get_object_or_404(PatientData, file_no=file_no)
#         handover = patient.handovers.filter(clinic='A & E', status='waiting_for_payment').first()

#         if handover:
#             context['patient'] = patient
#             context['handover'] = handover
#             service_name = 'new registration'
#             service = Services.objects.get(name=service_name)
#             context['service_name'] = service.name
#             context['service_price'] = service.price
#         else:
#             # Handle the case where no handover object is found
#             pass
#         return context

#     def form_valid(self, form):
#         file_no = self.kwargs.get('file_no')
#         patient = get_object_or_404(PatientData, file_no=file_no)
#         paypoints = Paypoint.objects.filter(patient=patient, status='pending')

#         for paypoint in paypoints:
#             paypoint.status = 'paid'
#             paypoint.save()

#         messages.success(self.request, 'Payment successful.')
#         return super().form_valid(form)
    # def form_valid(self, form):
    #     file_no = self.kwargs.get('file_no')
    #     patient = get_object_or_404(PatientData, file_no=file_no)
    #     handover = patient.handovers.filter(clinic='A & E', status='waiting_for_payment').first()

    #     if handover:
    #         new_registration_service = Services.objects.get(name='new registration')
    #         payment = Paypoint.objects.create(patient=patient, status='paid', service=new_registration_service)
            
    #         # Update handover status to 'waiting_for_vital_signs'
    #         handover.status = 'waiting_for_vital_signs'
    #         handover.save()
    #         messages.success(self.request, 'Payment successful. Patient handed over for vital signs.')
        
    #     return super().form_valid(form)


class PendingPayListView(LoginRequiredMixin, ListView):
    model = Paypoint
    template_name = 'ehr/revenue/pending_pay_list.html'

    def get_queryset(self):
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        return Paypoint.objects.filter(patient=patient, status='pending')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_no = self.kwargs.get('file_no')
        patient = get_object_or_404(PatientData, file_no=file_no)
        context['patient'] = patient
        return context
    


class PendingPayBaseListView(LoginRequiredMixin, TemplateView):
    template_name = 'ehr/revenue/paypoint_list_base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_type = self.kwargs.get('service_type')
        service_type_obj = ServiceType.objects.filter(name=service_type).first()

        if service_type_obj:
            payment_list = Paypoint.objects.filter(status='pending', service__type=service_type_obj)
            context['payment_list'] = payment_list
            context['department'] = service_type
        else:
            context['payment_list'] = []

        return context

    def render_to_response(self, context, **response_kwargs):
        service_type = self.kwargs.get('service_type')
        template_name = f"{service_type.lower()}_paypoint_list.html"
        return render(self.request, template_name, context)