# views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .filters import *
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *
import datetime
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from io import BytesIO
from django.template.loader import get_template
from django.conf import settings
import os
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q, Sum, Count, Value, DecimalField
from django.views.generic import UpdateView
from datetime import datetime
import io
from django.http import StreamingHttpResponse
from django.utils.dateparse import parse_date
from django.conf import settings
import xhtml2pdf.pisa as pisa
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.utils import timezone
from django.contrib.staticfiles import finders
from django.core.serializers.json import DjangoJSONEncoder # Handles Decimal, date, etc.
import json


class ExpenseRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='ACCOUNTING').exists()
    

class CompanyAccountRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='ACCOUNTING').exists()


def group_required(group_name):
    def decorator(view_func):
        @login_required
        @user_passes_test(lambda u: u.groups.filter(name=group_name).exists())
        def _wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
# -------------------------------------------------------------------
# PDF Utility Functions
# -------------------------------------------------------------------
def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    # Use the static folder configured in settings
    static_url = settings.STATIC_URL
    static_root = settings.STATIC_ROOT
    media_url = settings.MEDIA_URL
    media_root = settings.MEDIA_ROOT

    # Make sure that uri has leading slash
    if uri.startswith(static_url):
        path = os.path.join(static_root, uri.replace(static_url, ""))
    elif uri.startswith(media_url):
        path = os.path.join(media_root, uri.replace(media_url, ""))
    else:
        return uri  # Handle absolute/external URIs

    # Make sure that file exists
    if not os.path.isfile(path):
        raise Exception(f'Media URI must start with {static_url} or {media_url} - {path} not found')
    
    return path

def fetch_resources(uri, rel):
    """
    Handles fetching static and media resources when generating the PDF.
    """
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path

def generate_pdf_buffer(context, template_name):
    """
    Render a PDF from the given context and template using xhtml2pdf.
    Returns a BytesIO buffer or None on error.
    """
    template = get_template(template_name)
    html = template.render(context)
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(
        html, dest=buffer, encoding='utf-8', link_callback=fetch_resources
    )
    if pisa_status.err:
        return None
    buffer.seek(0)
    return buffer

def pdf_generator(buffer):
    """
    Streaming generator for sending PDF data.
    """
    chunk_size = 8192
    while True:
        chunk = buffer.read(chunk_size)
        if not chunk:
            break
        yield chunk


class ExpenseListView(ExpenseRequiredMixin,ListView):
    model = CompanyExpense
    template_name = 'accounting/expenses_list.html'
    context_object_name = 'expenses'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-updated')
        params = self.request.GET
        expense_id=self.request.GET.get('expense_id')

        if expense_id:
            return CompanyExpense.objects.filter(id=expense_id)

        elif search_query := params.get('q'):
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(payment_method__icontains=search_query) |
                Q(account_used__name__icontains=search_query) |
                Q(vendor__icontains=search_query) |
                Q(notes__icontains=search_query)
            )

        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        if start_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(created__gte=start_date)
            
        if end_date:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(created__lte=end_date)

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
                
        # Existing context
        context.update({
            'search_count': queryset.count(),
            'total_entry': self.model.objects.count(),
            'query': self.request.GET.get('q', ''),
            'start_date': self.request.GET.get('start_date', ''),
            'end_date': self.request.GET.get('end_date', ''),
            'today': timezone.now().date()
        })
        return context


def expense_autocomplete(request):
    query = request.GET.get('term', '')
    if query:
        expenses = CompanyExpense.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(payment_method__icontains=query) |
            Q(account_used__name__icontains=query) |
            Q(vendor__icontains=query) |
            Q(notes__icontains=query)

        )[:20]  # Limit results
        
        results = []
        for expense in expenses:
            display_name = f"{expense.account_used} - {expense.vendor}",
            expense = {
                'id': expense.id,
                'label': display_name,
                'value': display_name  # Send back the original search term
            }
            results.append(expense)
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)


class ExpenseCreateView(ExpenseRequiredMixin, CreateView):
    model = CompanyExpense
    form_class = ExpenseForm
    success_url = reverse_lazy('erp:expenses_list')
    template_name = 'accounting/expenses_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        try:
            with transaction.atomic():
                # Flag to record transaction
                form.instance._record_transaction = True
                response = super().form_valid(form)
                messages.success(self.request, f"Expense of {form.instance.amount} created successfully")
                return response
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

class ExpenseUpdateView(ExpenseRequiredMixin, UpdateView):
    model = CompanyExpense
    form_class = ExpenseForm
    template_name = 'accounting/expenses_form.html'
    success_url = reverse_lazy('erp:expenses_list')
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Flag to record transaction
                form.instance._record_transaction = True
                response = super().form_valid(form)
                messages.success(self.request, f"Expense updated successfully")
                return response
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class ExpenseDeleteView(ExpenseRequiredMixin, DeleteView):
    model = CompanyExpense
    template_name = 'accounting/confirm_delete.html'
    success_url = reverse_lazy('erp:expenses_list')
    
    def delete(self, request, *args, **kwargs):
        expense = self.get_object()
        try:
            with transaction.atomic():
                # Flag to record transaction
                expense._record_transaction = True
                response = super().delete(request, *args, **kwargs)
                messages.success(request, f"Expense of {expense.amount} deleted successfully")
                return response
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect(expense.get_absolute_url())
            


class CompanyAccountCreateView(CompanyAccountRequiredMixin, CreateView):
    model = CompanyAccount
    form_class = CompanyAccountForm
    success_url = reverse_lazy('erp:company_account_list')
    template_name = 'accounting/company_acct_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            with transaction.atomic():
                # Flag to record transaction
                form.instance._record_transaction = True
                response = super().form_valid(form)
                messages.success(self.request, f"Company account {form.instance.name} created successfully")
                return response
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # This will render the template with form errors properly displayed
        return self.render_to_response(self.get_context_data(form=form))


class CompanyAccountListView(CompanyAccountRequiredMixin,ListView):
    model = CompanyAccount
    template_name = 'accounting/company_acct_list.html'
    context_object_name = 'company_accounts'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('name')
        params = self.request.GET
        company_acct_id = self.request.GET.get('company_acct_id')

        if company_acct_id:
            return CompanyAccount.objects.filter(id=company_acct_id)

        elif search_query := params.get('q'):
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(account_number__icontains=search_query)
            )

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
                
        # Existing context
        context.update({
            'search_count': queryset.count(),
            'total_entry': self.model.objects.count(),
            'query': self.request.GET.get('q', ''),
            'today': timezone.now().date()
        })
        return context

def company_account_autocomplete(request):
    query = request.GET.get('term', '')
    if query:
        company_accts = CompanyAccount.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(name__icontains=query) |
            Q(account_number__icontains=query)
        )[:20]  # Limit results
        
        results = []
        for company_acct in company_accts:
            display_name = f"{company_acct.name} - {company_acct.account_number}"
            company_acct = {
                'id': company_acct.id,
                'label': display_name,
                'value': display_name
            }
            results.append(company_acct)
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)


class CompanyAccountUpdateView(CompanyAccountRequiredMixin, UpdateView):
    model = CompanyAccount
    form_class = CompanyAccountForm
    success_url = reverse_lazy('erp:company_account_list')
    template_name = 'accounting/company_acct_form.html'
    
    def form_invalid(self, form):
        # This will render the template with form errors properly displayed
        return self.render_to_response(self.get_context_data(form=form))

class FundAccountView(CompanyAccountRequiredMixin, FormView):
    template_name = 'accounting/fund_account.html'
    form_class = AccountTransactionForm
    
    def get_success_url(self):
        return reverse_lazy('erp:company_account_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = get_object_or_404(CompanyAccount, pk=self.kwargs['pk'])
        context['account'] = account
        context['transaction_type'] = 'Fund'
        return context
    
    def form_valid(self, form):
        account = get_object_or_404(CompanyAccount, pk=self.kwargs['pk'])
        amount = form.cleaned_data['amount']
        description = form.cleaned_data['description']
        
        try:
            account.update_balance(amount)
            
            # Optionally log the transaction if you have a Transaction model
            Transaction.objects.create(
                account=account,
                amount=amount,
                description=description,
                transaction_type='DEPOSIT',
                created_by=self.request.user
            )
            
            messages.success(self.request, f"Successfully added {amount} to {account.name}")
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
            
        return super().form_valid(form)

class DeductAccountView(CompanyAccountRequiredMixin, FormView):
    template_name = 'accounting/fund_account.html'
    form_class = AccountTransactionForm
    
    def get_success_url(self):
        return reverse_lazy('erp:company_account_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = get_object_or_404(CompanyAccount, pk=self.kwargs['pk'])
        context['account'] = account
        context['transaction_type'] = 'Deduct'
        return context
    
    def form_valid(self, form):
        account = get_object_or_404(CompanyAccount, pk=self.kwargs['pk'])
        amount = form.cleaned_data['amount']
        description = form.cleaned_data['description']
        
        try:
            account.deduct_balance(amount)
            
            # Optionally log the transaction if you have a Transaction model
            Transaction.objects.create(
                account=account,
                amount=-amount,  # Negative amount for deduction
                description=description,
                transaction_type='WITHDRAWAL',
                created_by=self.request.user
            )
            
            messages.success(self.request, f"Successfully deducted {amount} from {account.name}")
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
            
        return super().form_valid(form)
    

class AccountTransferView(CompanyAccountRequiredMixin, FormView):
    template_name = 'accounting/account_transfer.html'
    form_class = AccountTransferForm
    success_url = reverse_lazy('erp:company_account_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # If we're coming from a specific account, pre-select it as the source
        if 'pk' in self.kwargs:
            form.fields['source_account'].initial = self.kwargs['pk']
        return form
    
    def form_valid(self, form):
        source = form.cleaned_data['source_account']
        destination = form.cleaned_data['destination_account']
        amount = form.cleaned_data['amount']
        description = form.cleaned_data['description']
        
        try:
            # Use a database transaction to ensure atomicity
            with transaction.atomic():
                # Deduct from source account
                source.deduct_balance(amount)
                
                # Add to destination account
                destination.update_balance(amount)
                
                # Create transaction records
                Transaction.objects.create(
                    account=source,
                    amount=-amount,  # Negative amount for deduction
                    description=f"Transfer to {destination.name}: {description}",
                    transaction_type='WITHDRAWAL',
                    created_by=self.request.user
                )
                
                Transaction.objects.create(
                    account=destination,
                    amount=amount,
                    description=f"Transfer from {source.name}: {description}",
                    transaction_type='DEPOSIT',
                    created_by=self.request.user
                )
                
            messages.success(
                self.request, 
                f"Successfully transferred {amount} from {source.name} to {destination.name}"
            )
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
            
        return super().form_valid(form)


class TransactionListView(CompanyAccountRequiredMixin, ListView):
    model = Transaction
    template_name = 'accounting/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('account', 'created_by')
        
        # Apply filters from GET parameters
        params = self.request.GET
        
        # Account filter
        if account_id := params.get('account'):
            queryset = queryset.filter(account_id=account_id)
            
        # Transaction type filter
        if transaction_type := params.get('type'):
            queryset = queryset.filter(transaction_type=transaction_type)
            
        # Date range filter
        if start_date := params.get('start_date'):
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created__date__gte=start_date)
            except ValueError:
                pass
                
        if end_date := params.get('end_date'):
            try:
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created__date__lte=end_date)
            except ValueError:
                pass
                
        # Search by description
        if search_query := params.get('q'):
            queryset = queryset.filter(
                Q(description__icontains=search_query) |
                Q(account__name__icontains=search_query) |
                Q(created_by__username__icontains=search_query)
            )
            
        # Default ordering
        return queryset.order_by('-created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options to context
        context['accounts'] = CompanyAccount.objects.all()
        context['transaction_types'] = dict(
            DEPOSIT='Deposit',
            WITHDRAWAL='Withdrawal'
        )
        
        # Get filter values from request
        context.update({
            'selected_account': self.request.GET.get('account', ''),
            'selected_type': self.request.GET.get('type', ''),
            'start_date': self.request.GET.get('start_date', ''),
            'end_date': self.request.GET.get('end_date', ''),
            'search_query': self.request.GET.get('q', ''),
            'today': timezone.now().date()
        })
        
        # Add aggregated stats
        transactions = self.get_queryset()
        
        # Calculate totals
        deposits = transactions.filter(transaction_type='DEPOSIT')
        withdrawals = transactions.filter(transaction_type='WITHDRAWAL')
        
        context.update({
            'total_transactions': transactions.count(),
            'total_deposits': deposits.aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_withdrawals': withdrawals.aggregate(Sum('amount'))['amount__sum'] or 0,
            'net_movement': (deposits.aggregate(Sum('amount'))['amount__sum'] or 0) - 
                           (withdrawals.aggregate(Sum('amount'))['amount__sum'] or 0)
        })
        
        return context
    


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    # Check if the URI is a static file
    if uri.startswith(settings.STATIC_URL):
        path = uri.replace(settings.STATIC_URL, "")
        # First, try to find the file in STATIC_ROOT
        static_file = os.path.join(settings.STATIC_ROOT, path)
        if os.path.exists(static_file):
            return static_file
        # If not found in STATIC_ROOT, use Django's finders to locate the file
        result = finders.find(path)
        if result:
            return result
    
    # Check if the URI is a media file
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        if os.path.exists(path):
            return path
    
    # If the URI isn't handled above, return it unchanged
    return uri

def generate_pdf(template_src, context_dict):
    """Helper function to generate PDF from HTML template"""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # Pass the link_callback to help resolve image paths
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), 
        result, 
        link_callback=link_callback
    )
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse(f'Error generating PDF: {pdf.err}', status=400)

class UnderConstructionView(TemplateView):
    template_name = "accounting/page_under_construction.html"

class AccountingIndexView(TemplateView):
    template_name = "accounting/accounting.html"
