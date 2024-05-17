from ehr.views import DoctorRequiredMixin
from .filters import *
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
            return redirect('list')  # Redirect to the drug list view after successful creation
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
                    paypoint = Paypoint.objects.create(
                        user=request.user,
                        patient=patient,
                        service=instance.drug.name,
                        price=instance.drug.cost_price * instance.quantity,
                        status=False
                    )
                    instance.payment = paypoint
                    instance.save()
            return redirect(reverse_lazy('patient_details', kwargs={'file_no': file_no}))
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
# @login_required(login_url='login')
# def create_dispensary(request, file_no):
#     patient = get_object_or_404(PatientData, file_no=file_no)
#     dispensary_instances = Dispensary.objects.filter(patient=patient)
#     DispensaryFormSet = modelformset_factory(Dispensary, form=DispenseForm, extra=5)
#     formset = DispensaryFormSet(queryset=Dispensary.objects.none())  # Initialize with an empty queryset

#     if request.method == 'POST':
#         formset = DispensaryFormSet(request.POST)
#         if formset.is_valid():
#             for form in formset:
#                 if form.has_changed():
#                     instance = form.save(commit=False)
#                     instance.patient = patient
#                     instance.dispensed_by = request.user

#                     # Create Paypoint instance with status=False
#                     paypoint = Paypoint.objects.create(
#                         user=request.user,
#                         patient=patient,
#                         service=instance.drug.name,
#                         price=instance.drug.cost_price * instance.quantity,
#                         status=False
#                     )
#                     instance.payment = paypoint
#                     instance.save()  # Call save() after creating the Paypoint instance
            
#             return redirect(reverse_lazy('patient_details', kwargs={'file_no': file_no}))
#         else:
#             formset = DispensaryFormSet(queryset=Dispensary.objects.none())

#     context = {
#         'formset': formset,
#         'patient': patient,
#         'dispensary_instances': dispensary_instances,
#     }
#     return render(request, 'dispensary/dispense.html', context)
    

class DispenseUpdateView(PharmacyRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Dispensary
    template_name = 'dispensary/update_dispense.html'
    # form_class = DispenseUpdateForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Drug Dispensed Updated Successfully')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating Drug Dispensed')
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        messages.success(self.request, 'Dispensary ADDED')
        return self.object.patient.get_absolute_url()


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