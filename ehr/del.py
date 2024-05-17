@login_required(login_url='login')
def create_dispensary(request, file_no):
    patient = get_object_or_404(PatientData, file_no=file_no)
    dispensary_instances = Dispensary.objects.filter(patient=patient)
    DispensaryFormSet = modelformset_factory(Dispensary, form=DispenseForm, extra=5)

    if request.method == 'POST':
        formset = DispensaryFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    instance.patient = patient
                    instance.dispensed_by = request.user

                    # Create Paypoint instance with status=False
                    paypoint = Paypoint.objects.create(
                        user=request.user,
                        patient=patient,
                        service=instance.drug.name,
                        price=instance.drug.cost_price * instance.quantity,
                        status=False
                    )
                    instance.payment = paypoint
                    instance.save()  # Call save() after creating the Paypoint instance

            return redirect(reverse_lazy('patient_details', kwargs={'file_no': file_no}))
        else:
            formset = DispensaryFormSet(queryset=Dispensary.objects.none())

    context = {
        'formset': formset,
        'patient': patient,
        'dispensary_instances': dispensary_instances,
    }
    return render(request, 'dispensary/dispense.html', context)