from ehr.views import DoctorRequiredMixin
from .filters import *
from ehr.filters import *
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
import datetime
from django.http import HttpResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os
from django.utils.decorators import method_decorator 
from django.core.paginator import Paginator
from .decorators import  superuser_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.forms import modelformset_factory,inlineformset_factory
from django.db.models import Sum
from django.urls import reverse
from django.views.generic import CreateView, FormView, ListView, DetailView, UpdateView, View
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.base import TemplateView


class PharmacyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='pharmacist').exists()


def user_is_in(user):
    return not user.is_authenticated


class DispensaryView(PharmacyRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "dispensary/dispensary.html"

@login_required
def pharm_inventory(request):
    return render(request, 'inventory/inventory.html')

@login_required
def drugs_list(request):
    drugs = Drug.objects.all().order_by('-name')
    pgn=Paginator(drugs,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {'drugs': drugs,'po':po}
    return render(request, 'inventory/items_list.html', context)


@login_required
def records(request):
    records = Record.objects.all().order_by('-updated_at')
    pgn=Paginator(records,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {'records': records, 'po':po}
    return render(request, 'inventory/record.html', context)


@login_required
def drug_report(request):
    drugfilter=DrugFilter(request.GET, queryset=Drug.objects.all().order_by('-name'))    
    pgtn=drugfilter.qs
    pgn=Paginator(pgtn,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {'drugfilter': drugfilter,'po':po}
    return render(request, 'inventory/item_report.html', context)

def record_report(request):
    recordfilter = RecordFilter(request.GET, queryset=Record.objects.all().order_by('-updated_at'))
    filtered_queryset = recordfilter.qs
    total_quantity = filtered_queryset.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    if filtered_queryset.exists():
        first_drug=filtered_queryset.first().drug.pack_price
    else:
        first_drug=0
    total_price=total_quantity*first_drug
    total_appearance=filtered_queryset.count()
    pgn=Paginator(filtered_queryset,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {
        'recordfilter': recordfilter,
        'total_appearance': total_appearance,
        'total_price':total_price,
        'total_quantity':total_quantity,
        'po':po
    }
    return render(request, 'inventory/record_report.html', context)



@superuser_required
def worth(request):
    total_store_value = Drug.total_store_value()
    ndate = datetime.datetime.now()
    today = ndate.strftime('%d-%B-%Y: %I:%M %p')
    context = {'total_store_value': total_store_value,'today':today}
    return render(request, 'inventory/worth.html', context)


@login_required
def create_drug(request):
    if request.method == 'POST':
        form = DrugForm(request.POST)
        if form.is_valid():
            new_drug=form.save(commit=False)
            new_drug.added_by=request.user
            new_drug.save()
            return redirect('pharm:list')  # Redirect to the drug list view after successful creation
    else:
        form = DrugForm()
    return render(request, 'inventory/create_item.html', {'form': form})


@login_required
def create_record(request):
    RecordFormSet = modelformset_factory(Record, form=RecordForm, extra=5)

    if request.method == 'POST':
        formset = RecordFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.issued_by = request.user
                instance.save()
            return redirect('pharm:record')
    else:
        formset = RecordFormSet(queryset=Record.objects.none())

    return render(request, 'inventory/create_record.html', {'formset': formset})


def get_drugs_by_category(request, category_id):
    drugs = Drug.objects.filter(category_id=category_id)
    drug_list = [{'id': drug.id, 'name': drug.name} for drug in drugs]
    return JsonResponse({'drugs': drug_list})


def fetch_resources(uri, rel):
    """
    Handles fetching static and media resources when generating the PDF.
    """
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path


def drug_pdf(request):
    ndate = datetime.datetime.now()
    filename = ndate.strftime('on_%d/%m/%Y_at_%I.%M%p.pdf')
    drugfilter = DrugFilter(request.GET, queryset=Drug.objects.all())
    f=drugfilter.qs
    keys = [key for key, value in request.GET.items() if value]

    result = f"GENERATED ON: {ndate.strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}"

    context = {'f': f, 'pagesize': 'A4', 'orientation': 'Potrait','result':result,'keys':keys}

    response = HttpResponse(content_type='application/pdf', headers={'Content-Disposition': f'filename="gen_by_{request.user}_{filename}"'})
    buffer = BytesIO()

    pisa_status = pisa.CreatePDF(get_template('inventory/item_pdf.html').render(context), dest=buffer, encoding='utf-8', link_callback=fetch_resources)

    if not pisa_status.err:
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    return HttpResponse('Error generating PDF', status=500)


def record_pdf(request):
    ndate = datetime.datetime.now()
    filename = ndate.strftime('on_%d/%m/%Y_at_%I.%M%p.pdf')
    f = RecordFilter(request.GET, queryset=Record.objects.all()).qs
    total_quantity = f.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    if f.exists():
        first_drug=f.first().drug.pack_price
    else:
        first_drug=0
    total_price=total_quantity*first_drug
    total_appearance=f.count()

    keys = [key for key, value in request.GET.items() if value]
    result = f"GENERATED ON: {ndate.strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}"
    context = {'f': f, 'pagesize': 'A4', 'orientation': 'Potrait','result':result,'keys':keys,'total_appearance': total_appearance,'total_price':total_price,'total_quantity':total_quantity,}
    response = HttpResponse(content_type='application/pdf', headers={'Content-Disposition': f'filename="gen_by_{request.user}_{filename}"'})
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(get_template('inventory/record_pdf.html').render(context), dest=buffer, encoding='utf-8', link_callback=fetch_resources)

    if not pisa_status.err:
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    return HttpResponse('Error generating PDF', status=500)


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
                    # paypoint = Paypoint.objects.create(
                    #     user=request.user,
                    #     patient=patient,
                    #     service=instance.drug.name,
                    #     price=instance.drug.cost_price * instance.quantity,
                    #     status=False
                    # )
                    # instance.payment = paypoint
                    instance.save()
            return redirect(reverse_lazy('pharm:prescription_list'))
        else:
            # If formset is not valid, it will automatically contain the errors.
            pass
    else:
        formset = DispensaryFormSet(queryset=Dispensary.objects.none())

    context = {
        'formset': formset,
        'patient': patient,
        'dispensary_instances': dispensary_instances,
    }
    return render(request, 'dispensary/dispense.html', context)


@login_required(login_url='login')
def create_prescription(request, file_no):
    patient = get_object_or_404(PatientData, file_no=file_no)
    prescription_instances = Prescription.objects.filter(patient=patient)
    PrescriptionFormSet = modelformset_factory(Prescription, form=PrescriptionForm, extra=5)
    formset = PrescriptionFormSet(queryset=Dispensary.objects.none())  # Initialize with an empty queryset

    if request.method == 'POST':
        formset = PrescriptionFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.has_changed():
                    instance = form.save(commit=False)
                    instance.patient = patient
                    instance.prescribed_by = request.user

                    paypoint = Paypoint.objects.create(
                        user=request.user,
                        patient=patient,
                        service=instance.drug.name,
                        price=instance.drug.cost_price * instance.quantity,
                        status=False
                    )
                    instance.payment = paypoint
                    instance.save()
            messages.success(request,'drugs prescribed')
            return redirect(reverse_lazy('patient_details', kwargs={'file_no': file_no}))
        else:
            formset = PrescriptionFormSet(queryset=Prescription.objects.none())

    context = {
        'formset': formset,
        'patient': patient,
        'prescription_instances': prescription_instances,
    }
    return render(request, 'dispensary/prescription.html', context)
    

class DispenseListView(PharmacyRequiredMixin, LoginRequiredMixin, ListView):
    model=Dispensary
    template_name='dispensary/dispense_list.html'
    context_object_name='dispensed'
    paginate_by = 10

    def get_queryset(self):
        updated = super().get_queryset().order_by('-dispensed_date')
        dispense_filter = DispenseFilter(self.request.GET, queryset=updated)
        return dispense_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_dispensed = self.get_queryset().count()
        context['DispenseFilter'] = DispenseFilter(self.request.GET, queryset=self.get_queryset())
        context['total_dispensed'] = total_dispensed
        return context


class PrescriptionListView(PharmacyRequiredMixin, LoginRequiredMixin, ListView):
    model=Prescription
    template_name='dispensary/prescription_list.html'
    context_object_name='prescribed'
    paginate_by = 10
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")
    
    def get_queryset(self):
        updated = super().get_queryset().order_by('-updated')
        prescribe_filter = PrescriptionFilter(self.request.GET, queryset=updated)
        return prescribe_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_prescription = self.get_queryset().count()
        context['PrescriptionFilter'] = PrescriptionFilter(self.request.GET, queryset=self.get_queryset())
        context['total_prescription'] = total_prescription
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        return context


class PrescriptionUpdateView(UpdateView):
    model = Prescription
    template_name = 'dispensary/update_prescription.html'
    form_class = PrescriptionUpdateForm
    success_url=reverse_lazy('pharm:prescription_list')
    
    def form_valid(self, form):
        if form.is_valid():
            form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error')
        return self.render_to_response(self.get_context_data(form=form))
    

class PharmPayListView(ListView):
    model = Paypoint
    template_name = 'dispensary/pharmacy_transaction.html'
    context_object_name = 'pharm_pays'
    paginate_by = 10

    def get_queryset(self):
        updated = super().get_queryset().filter(pharm_payment__isnull=False).order_by('-updated')
        pay_filter = PayFilter(self.request.GET, queryset=updated)
        return pay_filter.qs
        # return Paypoint.objects.filter(pharm_payment__isnull=False).order_by('-updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        # Calculate total worth only for paid transactions
        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['payFilter'] = PayFilter(self.request.GET, queryset=self.get_queryset())
        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        return context  