from .filters import ItemFilter, RecordFilter
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
import datetime
from django.http import HttpResponse, JsonResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os
from django.core.paginator import Paginator
from .decorators import superuser_required
from django.db import transaction


@login_required
def index(request):
    return render(request, 'store/index.html')


@login_required
def items_list(request):
    items = Item.objects.all().order_by('-updated_at')
    pgn=Paginator(items,10)
    pn=request.GET.get('page')
    po=pgn.get_page(pn)

    context = {'items': items,'po':po}
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
def item_report(request):
    itemfilter=ItemFilter(request.GET, queryset=Item.objects.all().order_by('-updated_at'))    
    context = {'itemfilter': itemfilter}
    return render(request, 'store/item_report.html', context)


@login_required
def record_report(request):
    recordfilter=RecordFilter(request.GET, queryset=Record.objects.all().order_by('-updated_at'))    
    context = {'recordfilter':recordfilter}
    return render(request, 'store/record_report.html', context)


@superuser_required
def worth(request):
    total_store_value = Item.total_store_value()
    ndate = datetime.datetime.now()
    today = ndate.strftime('%d-%B-%Y at: %I:%M %p')
    context = {'total_store_value': total_store_value,'today':today}
    return render(request, 'store/worth.html', context)


@login_required
@transaction.atomic
def create_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.added_by = request.user
            new_item.save()
            return redirect('inventory:list')
    else:
        form = ItemForm()
    
    return render(request, 'store/create_item.html', {'form': form})


@login_required
@transaction.atomic
def create_record(request):
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            unit_id = form.cleaned_data['unit'].id
            item_id = form.cleaned_data['item'].id

            new_record = form.save(commit=False)
            new_record.issued_by = request.user
            new_record.unit_id = unit_id
            new_record.item_id = item_id
            new_record.save()
            return redirect('inventory:record')
    else:
        form = RecordForm()
    return render(request, 'store/create_record.html', {'form': form})


@login_required
@transaction.atomic
def restock(request):
    if request.method == 'POST':
        form = ReStockForm(request.POST)
        if form.is_valid():
            unit_id = form.cleaned_data['unit'].id
            item_id = form.cleaned_data['item'].id

            new_record = form.save(commit=False)
            new_record.issued_by = request.user
            new_record.unit_id = unit_id
            new_record.item_id = item_id
            new_record.save()
            return redirect('inventory:list')
    else:
        form = ReStockForm()
    return render(request, 'store/restock.html', {'form': form})


@login_required
def get_items_for_unit(request):
    unit_id = request.GET.get('unit_id')
    items = Item.objects.filter(unit_id=unit_id).values('id', 'name').order_by('name')
    data = list(items)
    return JsonResponse(data, safe=False)


def fetch_resources(uri, rel):
    """
    Handles fetching static and media resources when generating the PDF.
    """
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path


def item_pdf(request):
    ndate = datetime.datetime.now()
    filename = ndate.strftime('on_%d/%m/%Y_at_%I.%M%p.pdf')
    f = ItemFilter(request.GET, queryset=Item.objects.all()).qs

    result = ""
    for key, value in request.GET.items():
        if value:
            result+= f" <br>Generated on: {ndate.strftime('%d-%B-%Y at %I:%M %p')}</br>By: {request.user.username.upper()}"
    
    context = {'f': f, 'pagesize': 'A4', 'orientation': 'Potrait','result':result}
    response = HttpResponse(content_type='application/pdf', headers={'Content-Disposition': f'filename="Report__{filename}"'})
   
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

    result = ""
    for key, value in request.GET.items():
        if value:
            result+= f"<br>Generated on: {ndate.strftime('%d-%B-%Y at %I:%M %p')}</br>By: {request.user.username.upper()}"
    
    context = {'f': f, 'pagesize': 'A4', 'orientation': 'Potrait','result':result}
    response = HttpResponse(content_type='application/pdf', headers={'Content-Disposition': f'filename="Report__{filename}"'})
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(get_template('store/record_pdf.html').render(context), dest=buffer, encoding='utf-8', link_callback=fetch_resources)

    if not pisa_status.err:
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    return HttpResponse('Error generating PDF', status=500)