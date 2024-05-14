from .filters import DrugFilter, RecordFilter
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
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.forms import modelformset_factory
from django.db.models import Sum, F,ExpressionWrapper, FloatField

def user_is_in(user):
    return not user.is_authenticated


@method_decorator(user_passes_test(user_is_in, login_url='/'), name='dispatch')
class CustomLoginView(LoginView):
    template_name='login.html'
    success_url=reverse_lazy('/')


@login_required
def index(request):
    return render(request, 'store/index.html')


# @login_required
# def dashboard(request):
#     return render(request, 'store/dashboard.html')


@login_required
def drugs_list(request):
    drugs = Drug.objects.all().order_by('-name')
    pgn=Paginator(drugs,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {'drugs': drugs,'po':po}
    return render(request, 'store/items_list.html', context)


@login_required
def records(request):
    records = Record.objects.all().order_by('-updated_at')
    pgn=Paginator(records,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {'records': records, 'po':po}
    return render(request, 'store/record.html', context)


@login_required
def reports(request):
    return render(request, 'store/report.html')


@login_required
def drug_report(request):
    drugfilter=DrugFilter(request.GET, queryset=Drug.objects.all().order_by('-name'))    
    pgtn=drugfilter.qs
    pgn=Paginator(pgtn,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {'drugfilter': drugfilter,'po':po}
    return render(request, 'store/item_report.html', context)


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
    return render(request, 'store/record_report.html', context)



@superuser_required
def worth(request):
    total_store_value = Drug.total_store_value()
    ndate = datetime.datetime.now()
    today = ndate.strftime('%d-%B-%Y: %I:%M %p')
    context = {'total_store_value': total_store_value,'today':today}
    return render(request, 'store/worth.html', context)


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
    return render(request, 'store/create_item.html', {'form': form})


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
            return redirect('record')
    else:
        formset = RecordFormSet(queryset=Record.objects.none())

    return render(request, 'store/create_record.html', {'formset': formset})


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

    pisa_status = pisa.CreatePDF(get_template('store/item_pdf.html').render(context), dest=buffer, encoding='utf-8', link_callback=fetch_resources)

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

    pisa_status = pisa.CreatePDF(get_template('store/record_pdf.html').render(context), dest=buffer, encoding='utf-8', link_callback=fetch_resources)

    if not pisa_status.err:
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    return HttpResponse('Error generating PDF', status=500)