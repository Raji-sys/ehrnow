from .filters import *
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import *
from datetime import datetime
from django.http import HttpResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.forms import modelformset_factory, BaseModelFormSet
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import UpdateView, ListView, DetailView, TemplateView, CreateView
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Case, When, Value, CharField, Q
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from .models import Unit
from decimal import Decimal
from django.db.models import Sum, F
from ehr.filters import PayFilter
from .decorators import  superuser_required
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.db.models import Q
from ehr.models import Clinic
from datetime import datetime
from django.utils.dateparse import parse_date
from django.urls import reverse

def group_required(group_name):
    def decorator(view_func):
        @login_required
        @user_passes_test(lambda u: u.groups.filter(name=group_name).exists())
        def _wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def unit_group_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        unit_id = kwargs.get('unit_id')  # Use 'unit_id' instead of 'pk'
        if unit_id is None:
            raise PermissionDenied

        unit = Unit.objects.get(pk=unit_id)
        if request.user.groups.filter(name=unit.name).exists():
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return login_required(_wrapped_view)


class UnitGroupRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if hasattr(self, 'get_unit_for_mixin'):
            unit = self.get_unit_for_mixin()
        else:
            unit = get_object_or_404(Unit, pk=self.kwargs['pk'])
        return self.request.user.groups.filter(name=unit.name).exists()
    

class PharmacyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='pharmacist').exists()


def user_is_in(user):
    return not user.is_authenticated

@login_required
def index(request):
    today = timezone.now().date()
    six_months_later = today + timedelta(days=180)

    expiring_drugs_count = Drug.objects.filter(
        expiration_date__gt=today,
        expiration_date__lte=six_months_later
    ).count()

    context = {
        'expiring_drugs_count': expiring_drugs_count
    }
    return render(request, 'store/index.html', context)


class StoreGroupRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='STORE').exists()
    
class MainStoreDashboardView(LoginRequiredMixin, StoreGroupRequiredMixin,TemplateView):
    template_name = 'store/main_store_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        six_months_later = today + timedelta(days=180)

        expiring_drugs_count = Drug.objects.filter(
            expiration_date__gt=today,
            expiration_date__lte=six_months_later
        ).count()
        context['expiring_drugs_count'] = expiring_drugs_count
        return context


@group_required('STORE')
@transaction.atomic
def create_drug(request):
    if request.method == 'POST':
        form = DrugForm(request.POST)
        if form.is_valid():
            new_drug=form.save(commit=False)
            new_drug.added_by=request.user
            new_drug.save()
            messages.success(request,'drug added to inventory')
            return redirect('pharm:list')
    else:
        form = DrugForm()
    return render(request, 'store/create_item.html', {'form': form})


@group_required('STORE')
def drugs_list(request):
    drugs = Drug.objects.all().order_by('category')
    query = request.GET.get('q')
    
    if query:
        drugs = drugs.filter(
            Q(name__icontains=query) | Q(trade_name__icontains=query) | Q(category__name__icontains=query)
        )
    
    today = timezone.now().date()
    one_month_later = today + timedelta(days=31)
    three_months_later = today + timedelta(days=90)
    six_months_later = today + timedelta(days=180)
    
    for drug in drugs:
        if drug.expiration_date:
            if drug.expiration_date <= today:
                drug.expiry_status = 'expired'  # Drug has expired
            elif drug.expiration_date <= one_month_later:
                drug.expiry_status = 'urgent'  # Expiring within 31 days
            elif drug.expiration_date <= three_months_later:
                drug.expiry_status = 'critical'  # Expiring within 3 months
            elif drug.expiration_date <= six_months_later:
                drug.expiry_status = 'expiring_soon'  # Expiring within 6 months
            else:
                drug.expiry_status = 'ok'
        else:
            drug.expiry_status = 'unknown'
    
    paginator = Paginator(drugs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'po': page_obj,
        'query': query,
        'total_expiring_in_6_months': drugs.filter(expiration_date__lte=six_months_later).count(),
        'total_expiring_in_3_months': drugs.filter(expiration_date__lte=three_months_later).count(),
        'total_expiring_in_1_month': drugs.filter(expiration_date__lte=one_month_later).count(),
    }
    return render(request, 'store/items_list.html', context)

class DrugUpdateView(LoginRequiredMixin, StoreGroupRequiredMixin, UpdateView):
    model=Drug
    form_class=DrugForm
    template_name='store/create_item.html'
    success_url=reverse_lazy('pharm:list')
  
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        messages.success(self.request, "Drug updated successfully.")
        return super().form_valid(form)


class ExpiryNotificationView(LoginRequiredMixin, ListView):
    model = Drug
    template_name = 'store/expiry_notification.html'
    context_object_name = 'drugs'
    paginate_by = 10

    def get_queryset(self):
        today = timezone.now().date()
        six_months_later = today + timedelta(days=180)

        # Annotate the queryset with an expiration status
        queryset = Drug.objects.filter(
            expiration_date__lte=six_months_later
        ).annotate(
            status=Case(
                When(expiration_date__lte=today, then=Value('expired')),
                When(expiration_date__lte=today + timedelta(days=31), then=Value('urgent')),
                When(expiration_date__lte=today + timedelta(days=90), then=Value('critical')),
                When(expiration_date__lte=six_months_later, then=Value('expiring_soon')),
                default=Value('ok'),
                output_field=CharField(),
            )
        ).order_by('expiration_date')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(trade_name__icontains=query)|
            Q(category__name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        one_month_later = today + timedelta(days=31)
        three_months_later = today + timedelta(days=90)
        six_months_later = today + timedelta(days=180)

        queryset = self.get_queryset()

        context['total_expired'] = queryset.filter(expiration_date__lte=today).count()
        context['total_expiring_in_1_month'] = queryset.filter(expiration_date__gt=today, expiration_date__lte=one_month_later).count()
        context['total_expiring_in_3_months'] = queryset.filter(expiration_date__gt=one_month_later, expiration_date__lte=three_months_later).count()
        context['total_expiring_in_6_months'] = queryset.filter(expiration_date__gt=three_months_later, expiration_date__lte=six_months_later).count()
        context['query'] = self.request.GET.get('q', '')       

        return context

@group_required('STORE')
def drug_report(request):
    # Initialize filter and get filtered queryset
    drugfilter = DrugFilter(request.GET, queryset=Drug.objects.all().order_by('name'))    
    filtered_queryset = drugfilter.qs

    # Count the number of records in the filtered queryset
    total_appearance = filtered_queryset.count()

    # Pagination
    pgn = Paginator(filtered_queryset, 10)
    pn = request.GET.get('page')
    po = pgn.get_page(pn)

    # Calculate totals using model properties
    total_purchased_quantity = filtered_queryset.aggregate(Sum('total_purchased_quantity'))['total_purchased_quantity__sum'] or 0
    total_issued = sum(drug.total_issued for drug in filtered_queryset)
    total_quantity = sum(drug.current_balance for drug in filtered_queryset)
    total_value = sum(drug.total_value for drug in filtered_queryset)

    context = {
        'drugfilter': drugfilter,
        'po': po,
        'total_appearance': total_appearance,
        'total_quantity': total_quantity,
        'total_value': total_value,
    }
    
    return render(request, 'store/item_report.html', context)


@group_required('STORE')
def records(request):
    records = Record.objects.all().order_by('-updated_at')

    # Search functionality
    query = request.GET.get('q')
    if query:
        records = records.filter(
            Q(drug__name__icontains=query) |
            Q(drug__trade_name__icontains=query)|
            Q(category__name__icontains=query)|
            Q(unit_issued_to__name__icontains=query)
        )
    pgn=Paginator(records,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {'records': records, 'po':po,'query': query or ''}
    return render(request, 'store/record.html', context)

@group_required('STORE')
def create_record(request):
    RecordFormSet = modelformset_factory(Record, form=RecordForm, extra=5)
    if request.method == 'POST':
        formset = RecordFormSet(request.POST)
        if formset.is_valid():
            try:
                with transaction.atomic():
                    instances = formset.save(commit=False)
                    any_saved = False
                    for instance in instances:
                        if instance.drug and instance.quantity:
                            instance.issued_by = request.user
                            instance.save()
                            any_saved = True
                    
                    if any_saved:
                        messages.success(request, 'Drugs issued successfully.')
                        return redirect('pharm:record')
                    else:
                        messages.warning(request, 'No drugs were issued. Please fill in at least one form.')
            except ValidationError as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "There were errors in the form. Please check and try again.")
    else:
        formset = RecordFormSet(queryset=Record.objects.none())
    return render(request, 'store/create_record.html', {'formset': formset})



class RecordUpdateView(LoginRequiredMixin, UpdateView):
    model = Record
    form_class = RecordForm
    template_name = 'store/update_record.html'
    success_url = reverse_lazy('pharm:record')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                form.instance.issued_by = self.request.user
                self.object = form.save()
                messages.success(self.request, "Record updated successfully.")
                return super().form_valid(form)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating the record. Please check the form.")
        return super().form_invalid(form)
    
def get_dispense_drugs(request):
    """
    Returns a JSON response with drugs for autocomplete.
    Supports optional dispensary_id parameter to filter by inventory.
    """
    query = request.GET.get('q', '').strip()
    dispensary_id = request.GET.get('dispensary_id')
    
    # Base queryset
    drugs = Drug.objects.all()
    
    # Filter by dispensary inventory if provided
    if dispensary_id:
        try:
            dispensary = DispensaryLocker.objects.get(id=dispensary_id)
            drugs = drugs.filter(
                lockerinventory__locker=dispensary,
                lockerinventory__quantity__gt=0
            ).distinct()
        except DispensaryLocker.DoesNotExist:
            pass
    
    # Apply search filter if query provided
    if query:
        drugs = drugs.filter(
            Q(name__icontains=query) |
            Q(trade_name__icontains=query) |
            Q(supplier__icontains=query) |
            Q(strength__icontains=query)
        )
    
    # Limit results for performance
    drugs = drugs[:50]
    
    drug_list = [
        {
            'id': drug.id,
            'name': drug.name or '',
            'trade_name': drug.trade_name or '',
            'supplier': drug.supplier or '',
            'strength': drug.strength or '',
            'dosage_form': drug.dosage_form or '',
            'pack_size': drug.pack_size or '',
        }
        for drug in drugs
    ]
    return JsonResponse({'drugs': drug_list})

def get_drugs(request):
    """
    Returns a JSON response with drugs for autocomplete.
    """
    drugs = Drug.objects.all()
    drug_list = [
        {
            'id': drug.id,
            'name': drug.name,
            'trade_name': drug.trade_name,
            'supplier': drug.supplier,
            'strength': drug.strength,
        }
        for drug in drugs
    ]
    return JsonResponse({'drugs': drug_list})

@group_required('STORE')
def record_report(request):
    # Apply the filter to all records, ordered by most recently updated
    recordfilter = RecordFilter(request.GET, queryset=Record.objects.all().order_by('-updated_at'))
    filtered_queryset = recordfilter.qs

    # Calculate total quantity across all filtered records
    total_quantity = filtered_queryset.aggregate(models.Sum('quantity'))['quantity__sum'] or 0

    # Attempt to get the cost price of the first drug in the filtered queryset
    first_drug_cost = Decimal('0')
    if filtered_queryset.exists():
        first_drug = filtered_queryset.first().drug
        if first_drug and first_drug.cost_price is not None:
            first_drug_cost = first_drug.cost_price

    # Calculate total price (assuming all drugs have the same price as the first one)
    total_price = total_quantity * first_drug_cost

    # Count the number of records in the filtered queryset
    total_appearance = filtered_queryset.count()

    # Paginate the results
    paginator = Paginator(filtered_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'recordfilter': recordfilter,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'page_obj': page_obj
    }

    return render(request, 'store/record_report.html', context)


@group_required('STORE')
def restock(request):
    RestockFormSet = modelformset_factory(Restock, form=RestockForm, extra=5)

    if request.method == 'POST':
        formset = RestockFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.restocked_by = request.user
                instance.save()
            messages.success(request,'drugs restocked')
            return redirect('pharm:restocked')
    else:
        formset = RestockFormSet(queryset=Restock.objects.none())

    return render(request, 'store/restock.html', {'formset': formset})


class RestockUpdateView(LoginRequiredMixin, StoreGroupRequiredMixin,UpdateView):
    model=Restock
    form_class=RestockForm
    template_name='store/update_restock.html'
    success_url=reverse_lazy('restocked')
    success_message = "Drug restocked successfully."
    
    def form_valid(self, form):
        form.instance.restocked_by = self.request.user
        return super().form_valid(form)
    

@group_required('STORE')
def restocked_list(request):
    restock = Restock.objects.all().order_by('-updated')
    # Search functionality
    query = request.GET.get('q')
    if query:
        restock = restock.filter(
            Q(drug__name__icontains=query) |
            Q(drug__trade_name__icontains=query)|
            Q(category__name__icontains=query)
        )
    pgn=Paginator(restock,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {'restock': restock, 'po':po,'query':query or ''}
    return render(request, 'store/restocked_list.html', context)
    

@group_required('STORE')
def restock_report(request):
    restockfilter = RestockFilter(request.GET, queryset=Restock.objects.all().order_by('-updated'))
    filtered_queryset = restockfilter.qs
    total_quantity = filtered_queryset.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    if filtered_queryset.exists() and filtered_queryset.first().drug.cost_price:
        first_drug=filtered_queryset.first().drug.cost_price
    else:
        first_drug=0
    total_price=total_quantity*first_drug
    total_appearance=filtered_queryset.count()
    pgn=Paginator(filtered_queryset,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {
        'restockfilter': restockfilter,
        'total_appearance': total_appearance,
        'total_price':total_price,
        'total_quantity':total_quantity,
        'po':po
    }
    return render(request, 'store/restock_report.html', context)


def fetch_resources(uri, rel):
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path

def generate_pdf(context, template_name):
    template = get_template(template_name)
    html = template.render(context)
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer, encoding='utf-8', link_callback=fetch_resources)
    
    if pisa_status.err:
        return None
    
    buffer.seek(0)
    return buffer

def pdf_generator(buffer):
    chunk_size = 8192
    while True:
        chunk = buffer.read(chunk_size)
        if not chunk:
            break
        yield chunk


@group_required('STORE')
def drug_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    drugfilter = DrugFilter(request.GET, queryset=Drug.objects.all().order_by('-updated_at'))
    f = drugfilter.qs
    keys = [key for key, value in request.GET.items() if value]
    result = f"GENERATED ON: {ndate.strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}"
    context = {'f': f, 'pagesize': 'A4', 'orientation': 'Portrait', 'result': result, 'keys': keys}
    
    pdf_buffer = generate_pdf(context, 'store/item_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="gen_by_{request.user}_{filename}"'
    return response


@group_required('STORE')
def record_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    f = RecordFilter(request.GET, queryset=Record.objects.all()).qs
    total_quantity = f.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    
    if f.exists() and f.first().drug.cost_price:
        first_drug = f.first().drug.cost_price
    else:
        first_drug = 0
    
    total_price = total_quantity * first_drug
    total_appearance = f.count()
    keys = [key for key, value in request.GET.items() if value]
    result = f"GENERATED ON: {ndate.strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}"
    
    context = {
        'f': f,
        'pagesize': 'A4',
        'orientation': 'Portrait',
        'result': result,
        'keys': keys,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
    }
    
    pdf_buffer = generate_pdf(context, 'store/record_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="gen_by_{request.user}_{filename}"'
    return response


@group_required('STORE')
def restock_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    f = RestockFilter(request.GET, queryset=Restock.objects.all()).qs
    total_quantity = f.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    
    if f.exists() and f.first().drug.cost_price:
        first_drug = f.first().drug.cost_price
    else:
        first_drug = 0
    
    total_price = total_quantity * first_drug
    total_appearance = f.count()
    keys = [key for key, value in request.GET.items() if value]
    result = f"GENERATED ON: {ndate.strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}"
    
    context = {
        'f': f,
        'pagesize': 'A4',
        'orientation': 'Portrait',
        'result': result,
        'keys': keys,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
    }
    
    pdf_buffer = generate_pdf(context, 'store/restock_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="gen_by_{request.user}_{filename}"'
    return response


class StoreWorthView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return super().handle_no_permission()

    template_name = 'store/main_store_value.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now()
        context['total_store_value'] = Drug.total_store_value()
        context['total_store_quantity'] = Drug.total_store_quantity()
        return context

class UnitWorthView(LoginRequiredMixin, DetailView):
    model = Unit
    template_name = 'store/unit_value.html'
    context_object_name = 'unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unit = self.object
        context['today'] = timezone.now()

        store_value = sum(store.total_value for store in unit.unit_store.all() if store.total_value is not None)
        store_quantity = sum(store.quantity for store in unit.unit_store.all())

        locker_value = 0
        locker_quantity = 0
        if hasattr(unit, 'dispensary_locker'):
            locker_aggregate = unit.dispensary_locker.inventory.aggregate(
                value=Sum(F('drug__cost_price') * F('quantity')),
                quantity=Sum('quantity')
            )
            locker_value = locker_aggregate['value'] or 0
            locker_quantity = locker_aggregate['quantity'] or 0

        context['unit_worth'] = {
            'store_value': store_value,
            'store_quantity': store_quantity,
            'locker_value': locker_value,
            'locker_quantity': locker_quantity,
            'total_value': store_value + locker_value,
            'total_quantity': store_quantity + locker_quantity
        }
        return context

class InventoryWorthView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'store/worth.html'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        # You can customize this method to redirect non-superusers or show an error message
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now()

        # context['total_store_quantity'] = Drug.total_store_quantity()
        context['total_store_value'] = Drug.total_store_value()
        context['combined_unit_value'] = Unit.combined_unit_value()
        context['grand_total_value'] = Unit.grand_total_value()
        
        unit_worths = {}
        for unit in Unit.objects.all().order_by('name'):
            store_value = sum(store.total_value for store in unit.unit_store.all() if store.total_value is not None)
            locker_value = 0
            if hasattr(unit, 'dispensary_locker'):
                locker_value = unit.dispensary_locker.inventory.aggregate(
                    total=Sum(F('drug__cost_price') * F('quantity'))
                )['total'] or 0
            unit_worths[unit.name] = {
                'store_value': store_value,
                'locker_value': locker_value,
                'total_value': store_value + locker_value
            }
        
        context['unit_worths'] = unit_worths
        return context


class StoreListView(LoginRequiredMixin, ListView):
    model = Unit
    template_name = 'store/store_list.html'
    context_object_name = 'stores'
    paginate_by = 10  # Adjust as needed

    def get_queryset(self):
        return Unit.objects.all().order_by('name')
    

class UnitDashboardView(LoginRequiredMixin, UnitGroupRequiredMixin, DetailView):
    model = Unit
    template_name = 'store/unit_dashboard.html'
    context_object_name = 'store'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        unit_pk = self.kwargs.get('pk')
        
        # Base queryset matching your list view exactly
        base_queryset = Prescription.objects.filter(
            unit_id=unit_pk, 
            prescription_drugs__isnull=False,
            is_dispensed=False
        ).distinct()
        
        # Total incoming prescriptions (same as list view)
        context['incoming_count'] = base_queryset.count()
        
        # Unpaid prescriptions (no payment or payment not completed)
        context['unpaid_count'] = base_queryset.filter(
            Q(payment__isnull=True) | Q(payment__status=False)
        ).count()
        
        # Recent prescriptions (last 24 hours)
        time_threshold = timezone.now() - timedelta(hours=24)
        context['recent_count'] = base_queryset.filter(
            updated__gte=time_threshold
        ).count()
        
        return context

        
class UnitBulkLockerDetailView(LoginRequiredMixin, UnitGroupRequiredMixin, DetailView):
    model = Unit
    template_name = 'store/unit_bulk_locker.html'
    context_object_name = 'store'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unit_store_drugs = UnitStore.objects.filter(unit=self.object).select_related('drug').order_by('-updated_at')

        query = self.request.GET.get('q')
        if query:
            unit_store_drugs = unit_store_drugs.filter(
                Q(drug__name__icontains=query) |
                Q(drug__trade_name__icontains=query)|
                Q(drug__category__name__icontains=query)
            )        
        # Pagination
        paginator = Paginator(unit_store_drugs, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        today = timezone.now().date()
        one_month_later = today + timedelta(days=31)
        three_months_later = today + timedelta(days=90)
        six_months_later = today + timedelta(days=180)
        
        total_worth = 0
        total_expiring_in_1_month = 0
        total_expiring_in_3_months = 0
        total_expiring_in_6_months = 0
        
        for unit_store_drug in page_obj:
            total_worth += unit_store_drug.total_value
            unit_store_drug.restock_info = Restock.objects.filter(drug=unit_store_drug.drug).order_by('-date').first()
            
            if unit_store_drug.drug.expiration_date:
                if unit_store_drug.drug.expiration_date <= one_month_later:
                    total_expiring_in_1_month += unit_store_drug.quantity
                elif unit_store_drug.drug.expiration_date <= three_months_later:
                    total_expiring_in_3_months += unit_store_drug.quantity
                elif unit_store_drug.drug.expiration_date <= six_months_later:
                    total_expiring_in_6_months += unit_store_drug.quantity
        
        context['page_obj'] = page_obj
        context['total_worth'] = total_worth
        context['total_expiring_in_6_months'] = total_expiring_in_6_months
        context['total_expiring_in_3_months'] = total_expiring_in_3_months
        context['total_expiring_in_1_month'] = total_expiring_in_1_month
        context['today'] = today
        context['one_month_later'] = one_month_later
        context['three_months_later'] = three_months_later
        context['six_months_later'] = six_months_later
        context['query'] = self.request.GET.get('q', '')       

        return context


class UnitDispensaryLockerView(LoginRequiredMixin, UnitGroupRequiredMixin, DetailView):
    model = Unit
    template_name = 'store/unit_dispensary_locker.html'
    context_object_name = 'store'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dispensary_drugs = LockerInventory.objects.filter(locker__unit=self.object).select_related('drug').order_by('-updated')

        # Calculate total worth
        total_worth = dispensary_drugs.aggregate(
            total=Sum(F('drug__cost_price') * F('quantity'))
        )['total'] or 0
        query = self.request.GET.get('q')
        if query:
            dispensary_drugs = dispensary_drugs.filter(
                Q(drug__name__icontains=query) |
                Q(drug__trade_name__icontains=query)|
                Q(drug__category__name__icontains=query)
            )        
        # Order the drugs and paginate
        ordered_drugs = dispensary_drugs.order_by('drug__name')
        paginator = Paginator(ordered_drugs, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['dispensary_drugs'] = page_obj
        context['total_worth'] = total_worth
        context['page_obj'] = page_obj
        context['query'] = self.request.GET.get('q', '')       
        return context

class UnitTransferView(LoginRequiredMixin, UnitGroupRequiredMixin, DetailView):
    model = Unit
    template_name = 'store/unit_transfer.html'
    context_object_name = 'store'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch unit issue records where this unit is the issuing unit
        unit_issue_records = UnitIssueRecord.objects.filter(
            unit=self.object,
            issued_to__isnull=False, 
            issued_to_locker__isnull=True
        ).order_by('-date_issued')
        query = self.request.GET.get('q')
        if query:
            unit_issue_records = unit_issue_records.filter(
                Q(drug__name__icontains=query) |
                Q(drug__trade_name__icontains=query)|
                Q(drug__category__name__icontains=query)
            )        
        # Paginate the results
        paginator = Paginator(unit_issue_records, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['unit_issue_records'] = page_obj
        context['page_obj'] = page_obj
        context['query'] = self.request.GET.get('q', '')       

        return context


@unit_group_required
def unitissuerecord(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    
    # Create a custom formset that passes the issuing_unit to each form
    class CustomUnitIssueFormSet(BaseModelFormSet):
        def __init__(self, *args, **kwargs):
            self.issuing_unit = kwargs.pop('issuing_unit', None)
            super().__init__(*args, **kwargs)

        def _construct_form(self, i, **kwargs):
            kwargs['issuing_unit'] = self.issuing_unit
            return super()._construct_form(i, **kwargs)
    
    UnitIssueFormSet = modelformset_factory(
        UnitIssueRecord,
        form=UnitIssueRecordForm,
        formset=CustomUnitIssueFormSet,
        extra=2
        )

    if request.method == 'POST':
        formset = UnitIssueFormSet(request.POST, issuing_unit=unit)
        if formset.is_valid():
            try:
                with transaction.atomic():
                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.issued_by = request.user
                        instance.unit = unit
                        instance.save()
                        if instance.issued_to_locker:
                            locker_inventory, created = LockerInventory.objects.get_or_create(
                                locker=instance.issued_to_locker,
                                drug=instance.drug,
                                defaults={'quantity': 0}
                            )
                            locker_inventory.quantity += instance.quantity
                            locker_inventory.save()
                    messages.success(request, 'Successfully Transfered')
                    return redirect('pharm:unit_transfer', pk=unit_id)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        formset = UnitIssueFormSet(
            queryset=UnitIssueRecord.objects.none(),
            issuing_unit=unit,
            initial=[{'unit': unit}] * 2
        )
    return render(request, 'store/unitissuerecord_form.html', {'formset': formset, 'unit': unit})


class TransferUpdateView(LoginRequiredMixin,UnitGroupRequiredMixin,UpdateView):
    model = UnitIssueRecord
    form_class = UnitIssueRecordForm
    template_name = 'store/transfer_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['issuing_unit'] = self.object.unit
        return kwargs

    def get_success_url(self):
        return reverse_lazy('unit_transfer', kwargs={'pk': self.object.unit.pk})

    def form_valid(self, form):
        try:
            form.instance.issued_by = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, "Record updated successfully.")
            return response
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating the record. Please check the form.")
        return super().form_invalid(form)


@unit_group_required
def dispensaryissuerecord(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    unit_locker = DispensaryLocker.objects.filter(unit=unit).first()

    class CustomUnitIssueFormSet(BaseModelFormSet):
        def __init__(self, *args, **kwargs):
            self.issuing_unit = kwargs.pop('issuing_unit', None)
            super().__init__(*args, **kwargs)

        def _construct_form(self, i, **kwargs):
            kwargs['issuing_unit'] = self.issuing_unit
            return super()._construct_form(i, **kwargs)

    UnitIssueFormSet = modelformset_factory(
        UnitIssueRecord,
        form=DispensaryIssueRecordForm,
        formset=CustomUnitIssueFormSet,
        extra=5
    )

    if request.method == 'POST':
        formset = UnitIssueFormSet(request.POST, issuing_unit=unit)
        if formset.is_valid():
            try:
                with transaction.atomic():
                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.issued_by = request.user
                        instance.unit = unit
                        instance.save()
                        # Update locker inventory if issued to locker
                        if instance.issued_to_locker:
                            locker_inventory, created = LockerInventory.objects.get_or_create(
                                locker=instance.issued_to_locker,
                                drug=instance.drug,
                                defaults={'quantity': 0}
                            )
                            locker_inventory.quantity += instance.quantity
                            locker_inventory.save()
                    messages.success(request, 'Dispensary Locker Restocked Successfully')
                    return redirect('pharm:unit_bulk_locker', pk=unit_id)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
    else:
        formset = UnitIssueFormSet(
            queryset=UnitIssueRecord.objects.none(),
            issuing_unit=unit,
            initial=[{'unit': unit, 'issued_to_locker': unit_locker}] * 5
        )

    return render(request, 'store/create_dispensary_record.html', {'formset': formset, 'unit': unit})


@login_required
def unitissue_report(request, pk):
    unit = get_object_or_404(Unit, id=pk)
    
    # Get the current dispensary locker (you might need to adjust this based on your logic)
    current_dispensary_locker = DispensaryLocker.objects.filter(unit=unit).first()
    
    # Initialize the filter with the queryset and manually set the initial value
    unitissuefilter = UnitIssueFilter(
        request.GET, 
        queryset=UnitIssueRecord.objects.filter(unit=unit).order_by('-updated_at'),
        dispensary_locker=current_dispensary_locker
    )
    
    # Set initial value for the unit filter
    unitissuefilter.form.initial['unit'] = pk
    
    filtered_queryset = unitissuefilter.qs
    total_quantity = filtered_queryset.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    if filtered_queryset.exists() and filtered_queryset.first().drug.selling_price:
        first_drug = filtered_queryset.first().drug.selling_price
    else:
        first_drug = 0

    total_price = total_quantity * first_drug
    total_appearance = filtered_queryset.count()

    pgn = Paginator(filtered_queryset, 10)
    pn = request.GET.get('page')
    po = pgn.get_page(pn)

    context = {
        'unit': unit,
        'unitissuefilter': unitissuefilter,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'po': po,
        'current_dispensary_locker': current_dispensary_locker,
    }
    return render(request, 'store/unitissue_report.html', context)


@login_required
def unitissue_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    f = UnitIssueFilter(request.GET, queryset=UnitIssueRecord.objects.all()).qs
    total_quantity = f.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    
    if f.exists() and f.first().drug.selling_price:
        first_drug = f.first().drug.selling_price
    else:
        first_drug = 0
    
    total_price = total_quantity * first_drug
    total_appearance = f.count()
    keys = [key for key, value in request.GET.items() if value]
    result = f"GENERATED ON: {ndate.strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}"
    
    context = {
        'f': f,
        'pagesize': 'A4',
        'orientation': 'Portrait',
        'result': result,
        'keys': keys,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
    }
    
    pdf_buffer = generate_pdf(context, 'store/unitissue_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="gen_by_{request.user}_{filename}"'
    return response


@login_required
def transfer_report(request, pk):
    unit = get_object_or_404(Unit, id=pk)
    
    transferfilter = TransferFilter(
        request.GET, 
        queryset=UnitIssueRecord.objects.filter(unit=unit).order_by('-updated_at'),
        current_unit=unit
    )
    
    transferfilter.form.initial['unit'] = pk
    
    filtered_queryset = transferfilter.qs
    total_quantity = filtered_queryset.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    if filtered_queryset.exists() and filtered_queryset.first().drug.selling_price:
        first_drug = filtered_queryset.first().drug.selling_price
    else:
        first_drug = 0

    total_price = total_quantity * first_drug
    total_appearance = filtered_queryset.count()

    pgn = Paginator(filtered_queryset, 10)
    pn = request.GET.get('page')
    po = pgn.get_page(pn)

    context = {
        'unit': unit,
        'transferfilter': transferfilter,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'po': po
    }
    return render(request, 'store/transfer_report.html', context)


@login_required
def transfer_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    f = TransferFilter(request.GET, queryset=UnitIssueRecord.objects.all()).qs
    total_quantity = f.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    
    if f.exists() and f.first().drug.selling_price:
        first_drug = f.first().drug.selling_price
    else:
        first_drug = 0
    
    total_price = total_quantity * first_drug
    total_appearance = f.count()
    keys = [key for key, value in request.GET.items() if value]
    result = f"GENERATED ON: {ndate.strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}"
    
    context = {
        'f': f,
        'pagesize': 'A4',
        'orientation': 'Portrait',
        'result': result,
        'keys': keys,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
    }
    
    pdf_buffer = generate_pdf(context, 'store/transfer_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="gen_by_{request.user}_{filename}"'
    return response
    

@login_required
def dispenserecord(request, dispensary_id, patient_id, prescription_id):
    dispensary = get_object_or_404(DispensaryLocker, id=dispensary_id)
    patient = get_object_or_404(PatientData, id=patient_id)
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Create formset without category dependency
    DispensaryFormSet = modelformset_factory(
        DispenseRecord, 
        form=DispenseRecordForm, 
        extra=5
    )
    
    # Get the prescription for the patient
    try:
        prescription = Prescription.objects.filter(patient=patient).latest('prescribed_date')
    except Prescription.DoesNotExist:
        prescription = None
    
    if prescription:
        # Get the prescription drugs
        prescription_drugs = prescription.prescription_drugs.all()
    else:
        prescription_drugs = None

    if request.method == 'POST':
        formset = DispensaryFormSet(
            request.POST, 
            queryset=DispenseRecord.objects.none(), 
            form_kwargs={'dispensary': dispensary, 'patient': patient}
        )
        if formset.is_valid():
            try:
                with transaction.atomic():
                    instances = formset.save(commit=False)
                    for instance in instances:
                        # Skip empty forms
                        if not instance.drug:
                            continue
                            
                        instance.dispensary = dispensary
                        instance.patient = patient
                        instance.dispensed_by = request.user
                        instance.save()

                    # Mark the prescription as dispensed if we dispensed something
                    if any(instance.drug for instance in instances):
                        prescription.is_dispensed = True
                        prescription.save()

                    messages.success(request, 'Drugs dispensed successfully')
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('pharm:unit_dispensary', pk=dispensary.unit.id)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        formset = DispensaryFormSet(
            queryset=DispenseRecord.objects.none(), 
            form_kwargs={'dispensary': dispensary, 'patient': patient}
        )
    
    context = {
        'formset': formset,
        'dispensary': dispensary,
        'patient': patient,
        'prescription': prescription,
        'prescription_drugs': prescription_drugs
    }
    return render(request, 'store/dispense_form.html', context)

class DispenseRecordView(LoginRequiredMixin, UnitGroupRequiredMixin, ListView):
    model = DispenseRecord
    template_name = 'store/dispensed_list.html'
    context_object_name = 'dispensed_list'
    paginate_by = 5

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.dispensary_locker = get_object_or_404(DispensaryLocker, pk=kwargs['pk'])
        self.unit = self.dispensary_locker.unit

    def get_queryset(self):
        queryset = DispenseRecord.objects.filter(dispensary=self.dispensary_locker).order_by('-updated')
        self.filterset = DispenseFilter(self.request.GET, queryset=queryset)
        self.filterset.form.initial['dispensary'] = self.dispensary_locker.pk
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_queryset = self.get_queryset()
        
        context['total_dispensed'] = filtered_queryset.count()
                
        price_totals = filtered_queryset.aggregate(
            total_cost=Sum(F('quantity') * F('drug__cost_price')),
            total_selling=Sum(F('quantity') * F('drug__selling_price')),
            total_quantity=Sum('quantity')
        )

        context['total_cost_price'] = price_totals['total_cost'] or Decimal('0.00')
        context['total_selling_price'] = price_totals['total_selling'] or Decimal('0.00')
        context['total_profit'] = context['total_selling_price'] - context['total_cost_price']

        context['percentage'] = (
            (context['total_profit'] / context['total_cost_price']) * 100
        ) if context['total_cost_price'] > 0 else Decimal('0.00')

        context['total_quantity'] = price_totals['total_quantity'] or 0

        context['total_price'] = context['total_selling_price']
        
        context['dispensary_locker'] = self.dispensary_locker
        context['dispensefilter'] = self.filterset
        
        return context

    def get_unit_for_mixin(self):
        return self.unit
    
    
@login_required
def dispense_report(request, pk):
    dispensary = get_object_or_404(DispensaryLocker, id=pk)
    
    # Initialize the filter with the queryset and manually set the initial value
    dispensefilter = DispenseFilter(request.GET, queryset=DispenseRecord.objects.filter(dispensary=dispensary).order_by('-updated'))
    
    # Set initial value for the dispensary filter
    dispensefilter.form.initial['dispensary'] = pk
    
    filtered_queryset = dispensefilter.qs
    total_quantity = filtered_queryset.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    if filtered_queryset.exists() and filtered_queryset.first().drug.selling_price:
        first_drug = filtered_queryset.first().drug.selling_price
    else:
        first_drug = 0

    total_price = total_quantity * first_drug
    total_appearance = filtered_queryset.count()

    pgn = Paginator(filtered_queryset, 10)
    pn = request.GET.get('page')
    po = pgn.get_page(pn)

    context = {
        'dispensary':dispensary,
        'dispensefilter': dispensefilter,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'po': po
    }
    return render(request, 'store/dispense_report.html', context)


@login_required
def dispense_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    f = DispenseFilter(request.GET, queryset=DispenseRecord.objects.all()).qs
    total_quantity = f.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    
    if f.exists() and f.first().drug.selling_price:
        first_drug = f.first().drug.selling_price
    else:
        first_drug = 0
    
    total_price = total_quantity * first_drug
    total_appearance = f.count()
    keys = [key for key, value in request.GET.items() if value]
    result = f"GENERATED ON: {ndate.strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}"
    
    context = {
        'f': f,
        'pagesize': 'A4',
        'orientation': 'Portrait',
        'result': result,
        'keys': keys,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
    }
    
    pdf_buffer = generate_pdf(context, 'store/dispense_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="gen_by_{request.user}_{filename}"'
    return response


class BoxView(LoginRequiredMixin, UnitGroupRequiredMixin, DetailView):
    model = Unit
    template_name = 'store/unit_box.html'
    context_object_name = 'store'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch unit issue records where this unit is the issuing unit
        unit_issue_records = UnitIssueRecord.objects.filter(
            unit=self.object,
            moved_to__isnull=False, 
            issued_to_locker__isnull=True
        ).order_by('-date_issued')
        query = self.request.GET.get('q')
        if query:
            unit_issue_records = unit_issue_records.filter(
                Q(drug__name__icontains=query) |
                Q(drug__trade_name__icontains=query)|
                Q(drug__category__name__icontains=query)
            )        
        # Paginate the results
        paginator = Paginator(unit_issue_records, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['unit_issue_records'] = page_obj
        context['page_obj'] = page_obj
        context['query'] = self.request.GET.get('q', '')       
        return context

@unit_group_required
def boxrecord(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    
    # Create a custom formset that passes the issuing_unit to each form
    class CustomUnitIssueFormSet(BaseModelFormSet):
        def __init__(self, *args, **kwargs):
            self.issuing_unit = kwargs.pop('issuing_unit', None)
            super().__init__(*args, **kwargs)

        def _construct_form(self, i, **kwargs):
            kwargs['issuing_unit'] = self.issuing_unit
            return super()._construct_form(i, **kwargs)
    
    UnitIssueFormSet = modelformset_factory(
        UnitIssueRecord,
        form=BoxRecordForm,
        formset=CustomUnitIssueFormSet,
        extra=2
        )

    if request.method == 'POST':
        formset = UnitIssueFormSet(request.POST, issuing_unit=unit)
        if formset.is_valid():
            try:
                with transaction.atomic():
                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.issued_by = request.user
                        instance.unit = unit
                        instance.save()
                        if instance.issued_to_locker:
                            locker_inventory, created = LockerInventory.objects.get_or_create(
                                locker=instance.issued_to_locker,
                                drug=instance.drug,
                                defaults={'quantity': 0}
                            )
                            locker_inventory.quantity += instance.quantity
                            locker_inventory.save()
                    messages.success(request, 'DRUGS MOVED TO DAMAGE AND EXPIRY BOX')
                    return redirect('pharm:unit_box', pk=unit_id)
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        formset = UnitIssueFormSet(
            queryset=UnitIssueRecord.objects.none(),
            issuing_unit=unit,
            initial=[{'unit': unit}] * 2
        )
    return render(request, 'store/boxrecord_form.html', {'formset': formset, 'unit': unit})


class BoxUpdateView(LoginRequiredMixin,UnitGroupRequiredMixin,UpdateView):
    model = UnitIssueRecord
    form_class = BoxRecordForm
    template_name = 'store/box_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['issuing_unit'] = self.object.unit
        return kwargs

    def get_success_url(self):
        return reverse_lazy('unit_box', kwargs={'pk': self.object.unit.pk})

    def form_valid(self, form):
        try:
            form.instance.issued_by = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, "Record updated successfully.")
            return response
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error updating the record. Please check the form.")
        return super().form_invalid(form)


@login_required
def box_report(request, pk):
    unit = get_object_or_404(Unit, id=pk)
    
    boxfilter = BoxFilter(
        request.GET, 
        queryset=UnitIssueRecord.objects.filter(unit=unit).order_by('-updated_at'),
    )
    
    boxfilter.form.initial['unit'] = pk
    
    filtered_queryset = boxfilter.qs
    total_quantity = filtered_queryset.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    if filtered_queryset.exists() and filtered_queryset.first().drug.selling_price:
        first_drug = filtered_queryset.first().drug.selling_price
    else:
        first_drug = 0

    total_price = total_quantity * first_drug
    total_appearance = filtered_queryset.count()

    pgn = Paginator(filtered_queryset, 10)
    pn = request.GET.get('page')
    po = pgn.get_page(pn)

    context = {
        'unit': unit,
        'boxfilter': boxfilter,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'po': po
    }
    return render(request, 'store/box_report.html', context)


@login_required
def box_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    f = BoxFilter(request.GET, queryset=UnitIssueRecord.objects.all()).qs
    total_quantity = f.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    
    if f.exists() and f.first().drug.selling_price:
        first_drug = f.first().drug.selling_price
    else:
        first_drug = 0
    
    total_price = total_quantity * first_drug
    total_appearance = f.count()
    keys = [key for key, value in request.GET.items() if value]
    result = f"GENERATED ON: {ndate.strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}"
    
    context = {
        'f': f,
        'pagesize': 'A4',
        'orientation': 'Portrait',
        'result': result,
        'keys': keys,
        'total_appearance': total_appearance,
        'total_price': total_price,
        'total_quantity': total_quantity,
    }
    
    pdf_buffer = generate_pdf(context, 'store/box_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="gen_by_{request.user}_{filename}"'
    return response


@login_required
def return_drug(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    ReturnDrugFormSet = modelformset_factory(ReturnedDrugs, form=ReturnDrugForm, extra=2)
    
    if request.method == 'POST':
        formset = ReturnDrugFormSet(request.POST, queryset=ReturnedDrugs.objects.none(), form_kwargs={'unit': unit})
        if formset.is_valid():
            try:
                with transaction.atomic():
                    instances = formset.save(commit=False)
                    for instance in instances:
                        if instance.drug and instance.quantity:
                            instance.unit = unit
                            instance.received_by = request.user
                            instance.save()

                            # Update UnitStore
                            unit_store, created = UnitStore.objects.get_or_create(unit=unit, drug=instance.drug)
                            unit_store.quantity += instance.quantity
                            unit_store.save()

                    messages.success(request, 'Drugs returned successfully')
                    return redirect('pharm:return_drugs_list', unit_id=unit.id)

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        formset = ReturnDrugFormSet(queryset=ReturnedDrugs.objects.none(), form_kwargs={'unit': unit})
    
    return render(request, 'store/return_drugs.html', {'formset': formset, 'unit': unit})


class ReturnedDrugsListView(ListView):
    model = ReturnedDrugs
    template_name = 'store/return_list.html'
    context_object_name = 'returned_drugs'
    paginate_by = 10

    def get_queryset(self):
        unit_id = self.kwargs.get('unit_id')
        self.unit = get_object_or_404(Unit, id=unit_id)
        queryset= ReturnedDrugs.objects.filter(unit=self.unit).order_by('-updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(drug__name__icontains=query) |
                Q(drug__trade_name__icontains=query)|
                Q(drug__category__name__icontains=query) |
                Q(patient_info__icontains=query)
            )
        
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unit'] = self.unit  # Pass the unit to the template
        context['query'] = self.request.GET.get('q', '') 
        return context

@login_required
def return_report(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    returnfilter = ReturnDrugFilter(request.GET, queryset=ReturnedDrugs.objects.filter(unit=unit).order_by('-updated'))

    filtered_queryset = returnfilter.qs
    total_quantity = filtered_queryset.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
    total_appearance = filtered_queryset.count()

    pgn = Paginator(filtered_queryset, 10)
    pn = request.GET.get('page')
    po = pgn.get_page(pn)

    context = {
        'unit': unit,
        'returnfilter': returnfilter,
        'total_appearance': total_appearance,
        'total_quantity': total_quantity,
        'po': po
    }
    return render(request, 'store/return_drugs_report.html', context)

from ehr.models import VisitRecord


@login_required
def prescription_pdf(request, file_no, prescription_id):
    # Get the patient by file_no instead of id
    patient = get_object_or_404(PatientData, file_no=file_no)
    
    # Get the prescription by ID
    prescription = get_object_or_404(Prescription, id=prescription_id, patient=patient)
    
    # Generate filename using file_no
    ndate = datetime.now()
    filename = f"prescription_{prescription_id}_{file_no}__{ndate.strftime('%I_%M%p')}.pdf"
    
    # Rest of your PDF generation code remains the same
    context = {
        'prescription': prescription,
        'patient': patient,
        'pagesize': 'A4',
        'orientation': 'portrait',
        'generated_date': ndate.strftime('%d-%B-%Y at %I:%M %p'),
    }
    
    # Create HTTP response
    response = HttpResponse(
        content_type='application/pdf',
        headers={'Content-Disposition': f'inline; filename="{filename}"'}
    )
    
    template = get_template('store/prescription_pdf.html')
    html = template.render(context)
    
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(
        html,
        dest=buffer,
        encoding='utf-8',
        link_callback=fetch_resources
    )
    
    if not pisa_status.err:
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    
    return HttpResponse('Error generating PDF', status=500)


class PharmPayListView(ListView):
    model = Paypoint
    template_name = 'ehr/revenue/pharm_pay_list.html'
    context_object_name = 'pharm_pays'
    paginate_by = 10
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")

    def get_queryset(self):
        queryset = super().get_queryset().filter(pharm_payment__isnull=False).order_by('-updated')
        
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pay_total = self.get_queryset().count()

        paid_transactions = self.get_queryset().filter(status=True)
        total_worth = paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

        context['payFilter'] = PayFilter(self.request.GET, queryset=self.get_queryset())
        context['pay_total'] = pay_total
        context['total_worth'] = total_worth
        context['query'] = self.request.GET.get('q', '')       

        return context  

class PrescriptionListView(ListView):
    model = Prescription
    template_name = 'dispensary/prescriptions_list.html'
    paginate_by = 10
    def get_queryset(self):
        store_pk = self.kwargs.get('store_pk')
        if store_pk is None:
            messages.error(self.request, "No store PK provided")
            return []
        queryset = super().get_queryset().filter(unit_id=store_pk, prescription_drugs__isnull=False,is_dispensed=False).order_by('-updated').distinct()

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(patient__first_name__icontains=query) |
                Q(patient__last_name__icontains=query) |
                Q(patient__other_name__icontains=query) |
                Q(patient__file_no__icontains=query)|
                Q(patient__phone__icontains=query)|
                Q(patient__title__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store'] = get_object_or_404(Unit, pk=self.kwargs['store_pk'])
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       
        return context

from django.db import IntegrityError
class PrescriptionCreateView(LoginRequiredMixin, CreateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'dispensary/prescription_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.patient = get_object_or_404(PatientData, file_no=kwargs['file_no'])
        return super().dispatch(request, *args, **kwargs)

    def set_unit(self, prescription):
        latest_visit_record = VisitRecord.objects.filter(patient=self.patient).last()
        if latest_visit_record and latest_visit_record.clinic:
            clinic = latest_visit_record.clinic
            unit_name = clinic.name  # Assume unit follows the clinic naming convention
            unit = Unit.objects.filter(name__icontains=unit_name).first()
            if unit:
                prescription.unit = unit
            else:
                messages.error(self.request, f"No matching unit found for clinic {clinic.name}.")
        else:
            messages.error(self.request, "No visit record or associated clinic found for this patient.")
        return prescription

    @transaction.atomic
    def form_valid(self, form):
        prescription = form.save(commit=False)
        prescription.prescribed_by = self.request.user
        prescription.patient = self.patient
        prescription = self.set_unit(prescription)
        prescription.save()
        
        selected_drugs = self.request.POST.getlist('selected_drugs')
        selected_doses = self.request.POST.getlist('selected_doses')
        manual_drug_names = self.request.POST.getlist('manual_drug_names')
        manual_drug_doses = self.request.POST.getlist('manual_drug_doses')
        
        unique_drugs = set()
        
        # Process selected drugs (from database)
        for i, drug_id in enumerate(selected_drugs):
            try:
                if drug_id in unique_drugs:
                    messages.warning(self.request, f'Drug {drug_id} was already added and skipped.')
                    continue
                PrescriptionDrug.objects.create(
                    prescription=prescription,
                    drug_id=drug_id,
                    dosage=selected_doses[i]
                )
                unique_drugs.add(drug_id)
            except IntegrityError:
                messages.warning(self.request, f'Drug {drug_id} could not be added due to a duplicate.')
                continue
        
        # Process manual drug entries
        for i, drug_name in enumerate(manual_drug_names):
            try:
                if drug_name.lower() in [name.lower() for name in unique_drugs if isinstance(name, str)]:
                    messages.warning(self.request, f'Drug "{drug_name}" was already added and skipped.')
                    continue
                
                # Try to find existing drug by name first
                existing_drug = Drug.objects.filter(
                    Q(name__iexact=drug_name) | Q(trade_name__iexact=drug_name)
                ).first()
                
                if existing_drug:
                    # Use existing drug if found
                    PrescriptionDrug.objects.create(
                        prescription=prescription,
                        drug=existing_drug,
                        dosage=manual_drug_doses[i]
                    )
                    unique_drugs.add(str(existing_drug.id))
                else:
                    # Create new drug entry for manual entries
                    new_drug = Drug.objects.create(
                        name=drug_name,
                        # You might want to set default values for other required fields
                        # strength='', supplier='Manual Entry', etc.
                    )
                    PrescriptionDrug.objects.create(
                        prescription=prescription,
                        drug=new_drug,
                        dosage=manual_drug_doses[i]
                    )
                    unique_drugs.add(drug_name.lower())
                    
            except (IntegrityError, IndexError) as e:
                messages.warning(self.request, f'Manual drug "{drug_name}" could not be added: {str(e)}')
                continue
        
        messages.success(self.request, 'Prescription added successfully')
        return super().form_valid(form)
    def get_success_url(self):
        return self.object.patient.get_absolute_url()

from django.views.generic import UpdateView
from django.urls import reverse
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder # For serializing Decimal and other types
import json


class PrescriptionUpdateView(UpdateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'dispensary/prescription_update.html' # This is the template we updated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Prepare all_drugs_json for autocomplete
        all_drugs_queryset = Drug.objects.all() # Or any other filtering you need for available drugs
        drugs_data_for_js = []
        for drug in all_drugs_queryset:
            drugs_data_for_js.append({
                'id': drug.id,
                'name': drug.name,
                'strength': drug.strength if hasattr(drug, 'strength') else None, # Assuming strength might not always exist
                'selling_price': float(drug.selling_price) if drug.selling_price is not None else 0.0
            })
        context['all_drugs_json'] = json.dumps(drugs_data_for_js, cls=DjangoJSONEncoder)

        # Keep the existing logic for 'drugs' if any other part of the template still uses it,
        # though the primary drug selection now uses all_drugs_json.
        # For clarity, if 'drugs' is only for all_drugs_json, you might not need to pass it separately.
        context['drugs'] = all_drugs_queryset 


        # Calculate total price for each prescription drug (existing logic)
        prescription_drugs_on_form = self.object.prescription_drugs.all() # Use a different variable name
        prescription_drugs_with_total_price = []
        drugs_without_price_on_load = [] # Renamed to avoid conflict in messages later
        
        for pd in prescription_drugs_on_form:
            selling_price = getattr(pd.drug, 'selling_price', None)
            if selling_price is None or selling_price == 0:
                pd.total_price = 0 # Annotate the object for the template
                drugs_without_price_on_load.append(pd.drug.name)
            else:
                pd.total_price = selling_price * pd.quantity # Annotate for the template
            prescription_drugs_with_total_price.append(pd)
        
        context['prescription_drugs'] = prescription_drugs_with_total_price # Used by the table in the template
        # context['drugs_without_price_on_load'] = drugs_without_price_on_load # If you need to show this on page load

        # Calculate initial grand total price for all prescription drugs (existing logic)
        initial_grand_total_price = 0
        for pd in prescription_drugs_on_form: # Iterate over the same consistent list
            selling_price = getattr(pd.drug, 'selling_price', None)
            if selling_price is not None and selling_price > 0:
                initial_grand_total_price += selling_price * pd.quantity
        
        context['total_price'] = initial_grand_total_price # Used by the table grand total in the template
        return context

    def form_valid(self, form):
        prescription = form.save(commit=False)
        if not prescription.prescribed_by:
             prescription.prescribed_by = self.request.user
        prescription.save()

        drugs_to_keep_from_form = []
        
        # --- START MODIFIED SECTION FOR COLLECTING DRUG DATA ---
        indices_found = set()
        for key in self.request.POST.keys():
            if key.startswith('drug_') and not key.startswith('drug_search_input'): # Avoid main search input if named similarly
                parts = key.split('_')
                if len(parts) == 2: # Expecting drug_IDX
                    try:
                        indices_found.add(int(parts[1]))
                    except ValueError:
                        # Key might be 'drug_somethingelse', not 'drug_INDEX'
                        continue
        
        # print(f"Indices found in POST: {sorted(list(indices_found))}") # For debugging

        for index in sorted(list(indices_found)): # Process indices in order for consistency
            drug_id_str = self.request.POST.get(f'drug_{index}')
            quantity_str = self.request.POST.get(f'quantity_{index}')
            dose_str = self.request.POST.get(f'dose_{index}')

            # print(f"Processing index {index}: drug_id={drug_id_str}, quantity={quantity_str}") # For debugging

            if drug_id_str and quantity_str:  # Ensure essential data is present
                try:
                    # Validate quantity is a positive integer
                    quantity_val = int(quantity_str)
                    if quantity_val <= 0:
                        messages.error(self.request, f"Invalid quantity ({quantity_val}) submitted for one of the drug rows (index {index}). Quantity must be positive.")
                        continue # Skip this drug entry

                    drugs_to_keep_from_form.append({
                        'drug_id': int(drug_id_str),
                        'quantity': quantity_val,
                        'dosage': dose_str or ''
                    })
                except ValueError:
                    messages.error(self.request, f"Invalid data submitted for one of the drug rows (index {index}). Please check drug ID and quantity format.")
                    continue # Skip this entry due to conversion error
            # else:
                # Optional: Log or message if a drug_X was found but corresponding quantity_X was missing
                # print(f"Warning: Missing drug_id or quantity for index {index}")
        # --- END MODIFIED SECTION ---
        
        # print(f"Drugs to keep from form: {drugs_to_keep_from_form}") # For debugging

        prescription.prescription_drugs.all().delete()
        
        final_total_price = 0
        drugs_without_pricing_info = []
        
        for drug_data in drugs_to_keep_from_form:
            try:
                drug_instance = Drug.objects.get(id=drug_data['drug_id'])
                selling_price = getattr(drug_instance, 'selling_price', None)
                
                if selling_price is None or selling_price == 0:
                    drugs_without_pricing_info.append(drug_instance.name)
                else:
                    # Ensure selling_price is a number before multiplication
                    if isinstance(selling_price, (int, float)):
                        final_total_price += selling_price * drug_data['quantity']
                    else:
                        # Handle case where selling_price might be non-numeric (e.g. Decimal, needs conversion)
                        # This depends on your Drug model's selling_price field type
                        try:
                            final_total_price += float(selling_price) * drug_data['quantity']
                        except (ValueError, TypeError):
                            drugs_without_pricing_info.append(f"{drug_instance.name} (invalid price format)")


                PrescriptionDrug.objects.create(
                    prescription=prescription,
                    drug=drug_instance,
                    quantity=drug_data['quantity'],
                    dosage=drug_data['dosage']
                )
            except Drug.DoesNotExist:
                messages.warning(self.request, f"A drug with ID {drug_data['drug_id']} was not found and was skipped.")
                continue

        if hasattr(prescription, 'payment') and prescription.payment:
            prescription.payment.delete() 
            prescription.payment = None   

        if final_total_price > 0:
            paypoint = Paypoint.objects.create(
                user=self.request.user, 
                patient=prescription.patient,
                service='drug payment', 
                unit='pharmacy', 
                price=final_total_price,
                status=False 
            )
            prescription.payment = paypoint
            prescription.save() 
            
            if drugs_without_pricing_info:
                messages.warning(
                    self.request, 
                    f'Prescription costed successfully for  {final_total_price:,.2f}. Note: The following drugs have no/invalid selling price: {", ".join(drugs_without_pricing_info)}. Please proceed to make payment.'
                )
            else:
                messages.success(
                    self.request, 
                    f'Prescription costed successfully for  {final_total_price:,.2f}. Please proceed to make payment.'
                )
        else:
            if drugs_without_pricing_info:
                messages.error(
                    self.request, 
                    f'Prescription updated. No payment is required as all item(s) have no/invalid selling price or zero quantity: {", ".join(drugs_without_pricing_info)}. Please update drug prices/formats in inventory if needed.'
                )
            else:
                messages.info(
                    self.request, 
                    'Prescription updated. No payment is required as the total price is zero or no priced items were included.'
                )
        
        return_url = self.get_success_url()
        return redirect(return_url)


    def get_success_url(self):
        # Assuming you want to redirect to a detail view or list view.
        # If self.object.unit is how you get the store_pk:
        if hasattr(self.object, 'unit') and self.object.unit:
            return reverse('pharm:prescription_list', kwargs={'store_pk': self.object.unit.pk})
        # Fallback if unit is not available or you have a different structure
        return reverse('pharm:some_default_prescription_list_or_detail') # Adjust to a valid fallback URL name
        
class InPatientPrescriptionCreateView(PrescriptionCreateView):
    def set_unit(self, prescription):
        in_patient_unit = Unit.objects.filter(name__icontains='In-Patient').first()
        if in_patient_unit:
            prescription.unit = in_patient_unit
        else:
            messages.error(self.request, "No In-Patient unit found.")
        return prescription

