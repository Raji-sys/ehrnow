from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.views.generic.edit import UpdateView, CreateView, FormView
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, ListView
from django.views import View
from .forms import *
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .models import *
from .forms import *
from .filters import *
from django.contrib.auth import get_user_model
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime
from django.conf import settings
import os
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Count,Sum,Q
User = get_user_model()
from django.db import transaction
from django.db import reset_queries
reset_queries()
from ehr.models import PatientData
from django.utils.http import url_has_allowed_host_and_scheme
from datetime import datetime
from django.forms import modelformset_factory
from django.http import JsonResponse

class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='doctor').exists()


def log_anonymous_required(view_function, redirect_to=None):
    if redirect_to is None:
        redirect_to = '/'
    return user_passes_test(lambda u: not u.is_authenticated, login_url=redirect_to)(view_function)


def fetch_resources(uri, rel):
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT,uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.MEDIA_ROOT,uri.replace(settings.MEDIA_URL, ""))
    return path



@method_decorator(login_required(login_url='login'), name='dispatch')
class DashboardView(TemplateView):
    template_name = "dashboard.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class HematologyView(TemplateView):
    template_name = "hema/hematology.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class ChempathView(TemplateView):
    template_name = "chempath/chempath.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class MicrobiologyView(TemplateView):
    template_name = "micro/micro.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class SerologyView(TemplateView):
    template_name = "serology/serology.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class GeneralView(TemplateView):
    template_name = "general/general.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class ReportView(TemplateView):
    template_name = "report.html"

@method_decorator(login_required(login_url='login'), name='dispatch')
class RevenueView(TemplateView):
    template_name = "revenue.html"

    
class HematologyRequestListView(ListView):
    model=Testinfo
    template_name='hema/hematology_request.html'
    context_object_name='hematology_request'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(payment__unit__iexact="Hematology",cleared=False).order_by('-updated')
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
        context['query'] = self.request.GET.get('q', '')       
        return context 
    
class HematologyListView(ListView):
    model=Testinfo
    template_name='hema/hematology_list.html'
    context_object_name='hematology_results'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(payment__unit__iexact='Hematology',cleared=True).order_by('-updated')
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
        context['query'] = self.request.GET.get('q', '')       
        return context    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ReportView(ListView):
    model = Testinfo
    template_name = 'report.html'
    paginate_by = 10
    context_object_name = 'patient'

    def get_queryset(self):
        queryset = super().get_queryset()

        test_filter = TestFilter(self.request.GET, queryset=queryset)
        patient = test_filter.qs.order_by('-created')
        return patient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test_filter'] = TestFilter(self.request.GET, queryset=self.get_queryset())
        return context

@login_required
def report_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    f = TestFilter(request.GET, queryset=Testinfo.objects.all()).qs
    

    result = ""
    for key, value in request.GET.items():
        if value:
            result += f" {value.upper()}, Generated on: {ndate.strftime('%d-%B-%Y at %I:%M %p')}"
    
    context = {'f': f,'pagesize': 'A4','orientation': 'potrait', 'result': result,'generated_date': ndate.strftime('%d-%B-%Y at %I:%M %p')}
    
    response = HttpResponse(content_type='application/pdf',headers={'Content-Disposition': f'inline; filename="{filename}"'})
    html = get_template('report_pdf.html').render(context)
    
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer, encoding='utf-8', link_callback=fetch_resources)
    
    if not pisa_status.err:
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    
    return HttpResponse('Error generating PDF', status=500)


@login_required
def instance_pdf(request, id):
    # Get the specific instance or return 404
    f = get_object_or_404(Testinfo, id=id)
    
    # Generate filename with timestamp
    ndate = datetime.now()
    filename = f"record_{id}_{ndate.strftime('%d_%m_%Y_%I_%M%p')}.pdf"
    
    # Prepare context for the template
    context = {
        'f': f,
        'pagesize': 'A4',
        'orientation': 'portrait',
        'generated_date': ndate.strftime('%d-%B-%Y at %I:%M %p')
    }
    
    # Create HTTP response
    response = HttpResponse(
        content_type='application/pdf',
        headers={'Content-Disposition': f'inline; filename="{filename}"'}
    )
    
    # Get the template and render it with the context
    template = get_template('report_pdf.html')
    html = template.render(context)
    
    # Create PDF
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


class ChempathRequestListView(ListView):
    model=Testinfo
    template_name='chempath/chempath_request.html'
    context_object_name='chempath_request'
    paginate_by = 10

    def get_queryset(self):
        queryset=super().get_queryset().filter(payment__unit__iexact="Chemical pathology",cleared=False).order_by('-updated')
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
        context['query'] = self.request.GET.get('q', '')       
        return context    

class ChempathListView(ListView):
    model=Testinfo
    template_name='chempath/chempath_list.html'
    context_object_name='chempath_results'
    paginate_by = 10
    
    def get_queryset(self):
        queryset=super().get_queryset().filter(payment__unit__iexact='Chemical pathology',cleared=True).order_by('-updated')
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
        context['query'] = self.request.GET.get('q', '')       
        return context

class MicroRequestListView(ListView):
    model=Testinfo
    template_name='micro/micro_request.html'
    context_object_name='micro_request'
    paginate_by = 10

    def get_queryset(self):
        queryset=super().get_queryset().filter(payment__unit__iexact="Microbiology",cleared=False).order_by('-updated')
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
        context['query'] = self.request.GET.get('q', '')       
        return context

class MicroListView(ListView):
    model=Testinfo
    template_name='micro/micro_list.html'
    context_object_name='micro_results'
    paginate_by = 10

    def get_queryset(self):
        queryset=super().get_queryset().filter(payment__unit__iexact='Microbiology',cleared=True).order_by('-updated')
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
        context['query'] = self.request.GET.get('q', '')       
        return context

class SerologyRequestListView(ListView):
    model = Testinfo
    template_name = 'serology/serology_request.html'
    context_object_name = 'serology_request'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(payment__unit__iexact="Serology",cleared=False).order_by('-updated')
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
        context['query'] = self.request.GET.get('q', '')       
        return context


class SerologyListView(ListView):
    model=Testinfo
    template_name='serology/serology_list.html'
    context_object_name='serology_results'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(payment__unit__iexact='Serology',cleared=True).order_by('-updated')
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
        context['query'] = self.request.GET.get('q', '')       
        return context    

class GeneralRequestListView(ListView):
    model=GeneralTestResult
    template_name='general/general_request.html'
    context_object_name='general_request'
    paginate_by = 10

    def get_queryset(self):
        queryset=super().get_queryset().filter(cleared=False).order_by('-test_info__updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(test_info__patient__first_name__icontains=query) |
                Q(test_info__patient__last_name__icontains=query) |
                Q(test_info__patient__other_name__icontains=query) |
                Q(test_info__patient__file_no__icontains=query)|
                Q(test_info__patient__phone__icontains=query)|
                Q(test_info__patient__title__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')       
        return context    

class GeneralListView(ListView):
    model=GeneralTestResult
    template_name='general/general_list.html'
    context_object_name='general_results'
    paginate_by = 10

    def get_queryset(self):
        queryset=super().get_queryset().filter(test_info__payment__status=True,cleared=True).order_by('-test_info__updated')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(test_info__patient__first_name__icontains=query) |
                Q(test_info__patient__last_name__icontains=query) |
                Q(test_info__patient__other_name__icontains=query) |
                Q(test_info__patient__file_no__icontains=query)|
                Q(test_info__patient__phone__icontains=query)|
                Q(test_info__patient__title__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')       
        return context

class GeneralTestCreateView(LoginRequiredMixin, CreateView):
    model=GeneralTestResult
    form_class = GeneralTestForm
    template_name = 'general/general_result.html'
    
    def get_success_url(self):
        return self.object.test_info.patient.get_absolute_url()
    
    @transaction.atomic
    def form_valid(self, form):
        patient = PatientData.objects.get(file_no=self.kwargs['file_no'])
        
        # Create test_info only once
        test_info = Testinfo.objects.create(
            patient=patient,
            collected_by=self.request.user
        )
        form.instance.test_info = test_info

        general_result = form.save(commit=False)
        payment = Paypoint.objects.create(
            patient=patient,
            status=False,
            service=test_info.code,  # Use the test_info we created above
            unit='general',
            price=general_result.price,
        )         

        # Update the existing test_info instead of creating a new one
        test_info.payment = payment
        test_info.save()

        general_result.save()
        messages.success(self.request, 'general added successfully')
        return super().form_valid(form)



class GeneralResultUpdateView(LoginRequiredMixin, UpdateView):
    model=GeneralTestResult
    form_class = GeneralTestResultForm
    template_name = 'general/general_result.html'
    context_object_name = 'result'
    success_url = reverse_lazy('results:general_request')


    def get_object(self, queryset=None):
        patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        return GeneralTestResult.objects.get(test_info__patient=patient, pk=self.kwargs['pk'])

    @transaction.atomic
    def form_valid(self, form):
        form.instance.test_info.approved_by = self.request.user
        general_result = form.save(commit=False)
        general_result.save()
        messages.success(self.request, 'general result updated successfully')

        return super().form_valid(form)
 

@method_decorator(login_required(login_url='login'), name='dispatch')
class GeneralReportView(ListView):
    model=GeneralTestResult
    template_name = 'general/general_report.html'
    paginate_by = 10
    context_object_name = 'patient'

    def get_queryset(self):
        queryset = super().get_queryset()

        gen_filter = GenFilter(self.request.GET, queryset=queryset)
        patient = gen_filter.qs.order_by('-test_info__updated')

        return patient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gen_filter'] = GenFilter(self.request.GET, queryset=self.get_queryset())
        return context

@login_required
def general_report_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')  # Changed slashes to underscores

    f = GenFilter(request.GET, queryset=GeneralTestResult.objects.all()).qs
    # Get username safely
    username = request.user.username.upper() if hasattr(request.user, 'username') else "UNKNOWN USER"
    user=request.user

    result = ""
    for key, value in request.GET.items():
        if value:
            result += f" {value.upper()}, Generated on: {ndate.strftime('%d-%B-%Y at %I:%M %p')}, By: {username}"
    
    context = {
        'user':user,
        'f': f, 
        'pagesize': 'A4',
        'orientation': 'landscape', 
        'result': result,
        'username': username,
        'generated_date': ndate.strftime('%d-%B-%Y at %I:%M %p')
    }
    
    response = HttpResponse(content_type='application/pdf',
                           headers={'Content-Disposition': f'inline; filename="{filename}"'})
    
    html = get_template('gen_pdf.html').render(context)
    
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer, encoding='utf-8', link_callback=fetch_resources)
    
    if not pisa_status.err:
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    
    return HttpResponse('Error generating PDF', status=500)


# class PathologyPayListView(ListView):
#     model = Paypoint
#     template_name = 'revenue/pathology_pay_list.html'
#     paginate_by = 10
#     context_object_name = 'pathology_pays'  # Add this to match your template

#     def get_queryset(self):
#         return Paypoint.objects.filter(test_payments__isnull=False,).order_by('-updated')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         pathology_pays=self.get_queryset()
#         pathology_pay_total = pathology_pays.count()
#         pathology_paid_transactions = pathology_pays.filter(status=True)
#         pathology_total_worth = pathology_paid_transactions.aggregate(total_worth=Sum('price'))['total_worth'] or 0

#         context['pathology_pay_total'] = pathology_pay_total

#         context['pathology_total_worth'] = pathology_total_worth
#         return context
class PathologyPayListView(ListView):
    model = Paypoint
    template_name = 'revenue/pathology_pay_list.html'
    paginate_by = 10
    context_object_name = 'pathology_pays'
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy("pay_list")


    def get_queryset(self):
        queryset = super().get_queryset().filter(lab_payment__isnull=False).select_related('patient', 'user').distinct().order_by('-updated')
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
        pathology_pays = self.get_queryset()
        
        # Calculate totals using distinct counts
        pathology_pay_total = pathology_pays.distinct().count()
        pathology_paid_transactions = pathology_pays.filter(status=True).distinct()
        pathology_total_worth = pathology_paid_transactions.aggregate(
            total_worth=Sum('price'))['total_worth'] or 0
            
        context['pathology_pay_total'] = pathology_pay_total
        context['pathology_total_worth'] = pathology_total_worth
        context['next'] = self.request.GET.get('next', reverse_lazy("pay_list"))
        context['query'] = self.request.GET.get('q', '')       

        return context
          
class BaseTestView(LoginRequiredMixin):
    template_name = 'shared_test_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# hematology 
class BloodGroupCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Blood Group')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            blood_group = BloodGroup.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Blood Group test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Blood Group test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class GenotypeCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Genotype')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            geno = Genotype.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Genotype test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Genotype test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class FBCCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Full Blood Count')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            fbc = FBC.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'FBC test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating FBC test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

# chempath 
class UECreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Urea & Electrolyte')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            ue = UreaAndElectrolyte.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'UREA & ELCTROLYTE test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating UREA & ELCTROLYTE test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class LiverFunctionCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Liver Function')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            liver_function = LiverFunction.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Liver Function test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Liver Function test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class LipidProfileCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Lipid Profile')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            lipid_profile = LipidProfile.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Lipid Profile test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Lipid Profile test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class SerumProteinsCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Serum Proteins')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            serum_proteins = SerumProteins.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Serum Proteins test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Serum Proteins test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class CerebroSpinalFluidCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Cerebro Spinal Fluid')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            cerebro_spinal_fluid = CerebroSpinalFluid.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Cerebro Spinal Fluid test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Cerebro Spinal Fluid test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class BoneChemistryCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Bone Chemistry')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            bone_chemistry = BoneChemistry.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Bone Chemistry test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Bone Chemistry test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class MiscellaneousChempathTestsCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Miscellaneous Chempath Tests')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            miscellaneous_chempath_tests = MiscellaneousChempathTests.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Miscellaneous Chempath Tests created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Miscellaneous Chempath Tests: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class BloodGlucoseCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Blood Glucose')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            blood_glucose = BloodGlucose.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Blood Glucose test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Blood Glucose test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

# serology 
class WidalCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='MP/Widal')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            widal = Widal.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Widal test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Widal test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))
    
class RheumatoidFactorCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Rheumatoid Factor')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            rheumatoid_factor = RheumatoidFactor.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Rheumatoid Factor test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Rheumatoid Factor test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class HepatitisBCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Hepatitis B')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            hpb = HPB.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Hepatitis B test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Hepatitis B test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class HepatitisCCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Hepatitis C')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            hcv = HCV.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Hepatitis C test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Hepatitis C test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class VDRLCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='VDRL')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            vdrl = VDRL.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'VDRL test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating VDRL test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class MantouxCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Mantoux')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            mantoux = Mantoux.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Mantoux test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Mantoux test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class AsoTitreCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Aso Titre')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            aso_titre = AsoTitre.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Aso Titre test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Aso Titre test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class CRPCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='CRP')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            crp = CRP.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'CRP test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating CRP test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class HIVScreeningCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='HIV Screening')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            hiv_screening = HIVScreening.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'HIV Screening test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating HIVScreening test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


#microbiology
class UrineMicroscopyCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Urine MCS')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            urine_microscopy = UrineMicroscopy.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Urine Microscopy test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Urine Microscopy test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class HVSCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='HVS MCS')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            hvs = HVS.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'HVS test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating HVS test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class StoolCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Stool MCS')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            stool = Stool.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Stool test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Stool test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class SwabPusAspirateCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='SWAB PUS ASPIRATE (MCS)')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            swab_pus_aspirate_mcs = Swab_Pus_Aspirate_MCS.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'swab pus aspirate test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating SWAB PUS ASPIRATE (MCS) test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class BloodCultureCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Blood Culture')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            blood_culture = BloodCulture.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Blood Culture test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Blood Culture test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class OccultBloodCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Occult Blood')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            occult_blood = OccultBlood.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Occult Blood test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Occult Blood test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class SputumMCSCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Sputum MCS')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            sputum_mcs = SputumMCS.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Sputum MCS test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Sputum MCS test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class GramStainCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Gram Stain')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            gram_stain = GramStain.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Gram Stain test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Gram Stain test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class ZNStainCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='ZN Stain')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            zn_stain = ZNStain.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'ZN Stain test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating ZN Stain test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class SemenAnalysisCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Semen Analysis')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            semen_analysis = SemenAnalysis.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Semen Analysis test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Semen Analysis Stain test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class UrinalysisCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Urinalysis')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            urinalysis = Urinalysis.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Urinalysis test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Urinalysis test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))

class PregnancyCreateView(View):
    @transaction.atomic
    def get(self, request, file_no):
        try:
            patient = get_object_or_404(PatientData, file_no=file_no)
            generic_test = get_object_or_404(GenericTest, name__iexact='Pregnancy Test')
            
            # Create Paypoint first
            payment = Paypoint.objects.create(
                patient=patient,
                status=False,
                unit=generic_test.lab,
                service=generic_test.name,
                price=generic_test.price,
            )
            
            # Now create Testinfo with the payment
            test_info = Testinfo.objects.create(
                patient=patient,
                collected_by=request.user,
                payment=payment
            )
            
            pregnancy = Pregnancy.objects.create(
                test=generic_test,
                test_info=test_info
            )

            messages.success(request, 'Pregnancy test created successfully')
        except Exception as e:
            messages.error(request, f'Error creating Pregnancy test: {str(e)}')
        
        return redirect(reverse('patient_details', kwargs={'file_no': file_no}))


class BaseLabResultUpdateView(UpdateView):
    template_name = 'shared_test_form.html'
    def get_success_url(self):
        messages.success(self.request, f'{self.model.__name__} result added successfully')
        next_url = self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
            return next_url
        return reverse_lazy("results:dashboard")
    
    def get_object(self, queryset=None):
        patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        test_info = get_object_or_404(Testinfo, patient=patient, pk=self.kwargs['test_info_pk'])
        return get_object_or_404(self.model, test_info=test_info)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.test_info.nature_of_specimen = self.request.POST.get('nature_of_specimen')
        instance.test_info.cleared = True
        instance.test_info.approved_by = self.request.user
        instance.test_info.save()
        instance.save()
        return super().form_valid(form)


class BloodGroupUpdateView(BaseLabResultUpdateView):
    model = BloodGroup
    form_class = BloodGroupForm

# hematology 
class BloodGroupUpdateView(BaseLabResultUpdateView):
    model = BloodGroup
    form_class = BloodGroupForm


class GenotypeUpdateView(BaseLabResultUpdateView):
    model = Genotype
    form_class = GenotypeForm


class FBCUpdateView(BaseLabResultUpdateView):
    model = FBC
    form_class = FBCForm

# chempath 
class UreaAndElectrolyteUpdateView(BaseLabResultUpdateView):
    model = UreaAndElectrolyte
    form_class = UreaAndElectrolyteForm

class LiverFunctionUpdateView(BaseLabResultUpdateView):
    model = LiverFunction
    form_class = LiverFunctionForm


class LipidProfileUpdateView(BaseLabResultUpdateView):
    model = LipidProfile
    form_class = LipidProfileForm


class SerumProteinsUpdateView(BaseLabResultUpdateView):
    model = SerumProteins
    form_class = SerumProteinsForm


class CerebroSpinalFluidUpdateView(BaseLabResultUpdateView):
    model = CerebroSpinalFluid
    form_class = CerebroSpinalFluidForm


class BoneChemistryUpdateView(BaseLabResultUpdateView):
    model = BoneChemistry
    form_class = BoneChemistryForm


class BloodGlucoseUpdateView(BaseLabResultUpdateView):
    model = BloodGlucose
    form_class = BloodGlucoseForm


class MiscellaneousChempathTestsUpdateView(BaseLabResultUpdateView):
    model = MiscellaneousChempathTests
    form_class = MiscellaneousChempathTestsForm


#SEROLOGY TEST
class WidalUpdateView(BaseLabResultUpdateView):
    model = Widal
    form_class = WidalForm


class RheumatoidFactorUpdateView(BaseLabResultUpdateView):
    model = RheumatoidFactor
    form_class = RheumatoidFactorForm


class HepatitisBUpdateView(BaseLabResultUpdateView):
    model = HPB
    form_class = HepatitisBForm


class HepatitisCUpdateView(BaseLabResultUpdateView):
    model = HCV
    form_class = HepatitisCForm


class VDRLUpdateView(BaseLabResultUpdateView):
    model = VDRL
    form_class = VDRLForm


class MantouxUpdateView(BaseLabResultUpdateView):
    model = Mantoux
    form_class = MantouxForm


class AsoTitreUpdateView(BaseLabResultUpdateView):
    model = AsoTitre
    form_class = AsoTitreForm


class CRPUpdateView(BaseLabResultUpdateView):
    model = CRP
    form_class = CRPForm


class HIVScreeningUpdateView(BaseLabResultUpdateView):
    model = HIVScreening
    form_class = HIVScreeningForm


#MICROBIOLOGY
class UrineMicroscopyUpdateView(BaseLabResultUpdateView):
    model = UrineMicroscopy
    form_class = UrineMicroscopyForm


class HVSUpdateView(BaseLabResultUpdateView):
    model = HVS
    form_class = HVSForm


class StoolUpdateView(BaseLabResultUpdateView):
    model = Stool
    form_class = StoolForm


class BloodCultureUpdateView(BaseLabResultUpdateView):
    model = BloodCulture
    form_class = BloodCultureForm


class OccultBloodUpdateView(BaseLabResultUpdateView):
    model = OccultBlood
    form_class = OccultBloodForm


class SputumMCSUpdateView(BaseLabResultUpdateView):
    model = SputumMCS
    form_class = SputumMCSForm


class GramStainUpdateView(BaseLabResultUpdateView):
    model = GramStain
    form_class = GramStainForm

class SwabPusAspirateUpdateView(BaseLabResultUpdateView):
    model = Swab_Pus_Aspirate_MCS
    form_class = Swab_pus_asiprate_mcsForm


class ZNStainUpdateView(BaseLabResultUpdateView):
    model = ZNStain
    form_class = ZNStainForm


class SemenAnalysisUpdateView(BaseLabResultUpdateView):
    model = SemenAnalysis
    form_class = SemenAnalysisForm


class UrinalysisUpdateView(BaseLabResultUpdateView):
    model = Urinalysis
    form_class = UrinalysisForm


class PregnancyUpdateView(BaseLabResultUpdateView):
    model = Pregnancy
    form_class = PregnancyForm


class LabTestingCreateView(DoctorRequiredMixin, FormView):
    template_name = 'ehr/revenue/labtesting.html'
    form_class = LabTestingForm
    
    def get_form(self):
        LabTestingFormSet = modelformset_factory(
            LabTesting, 
            form=LabTestingForm, 
            extra=10
        )
        if self.request.method == 'POST':
            return LabTestingFormSet(self.request.POST)
        return LabTestingFormSet(queryset=LabTesting.objects.none())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_form()
        context['patient'] = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
        context['get_lab_url'] = reverse('results:get_lab', kwargs={'lab_name': 'PLACEHOLDER'})
        return context

    def post(self, request, *args, **kwargs):
        formset = self.get_form()
        print("POST Data:", request.POST)  # Debug print
        print("Formset is valid:", formset.is_valid())  # Debug print
        if not formset.is_valid():
            print("Formset errors:", formset.errors)  # Debug print
        if formset.is_valid():
            return self.formset_valid(formset)
        return self.formset_invalid(formset)

    @transaction.atomic
    def formset_valid(self, formset):
        patient = get_object_or_404(PatientData, file_no=self.kwargs['file_no'])
            
        labtest = LabTest.objects.create(
            user=self.request.user, 
            patient=patient,
        )
        total_amount = 0
        instances = formset.save(commit=False)
        
        for instance in instances:
            if instance.total_item_price:  # Only process non-empty forms
                instance.labtest = labtest
                total_amount += instance.total_item_price
                instance.save()
        
        labtest.total_amount = total_amount
        labtest.save()

        paypoint = Paypoint.objects.create(
            user=self.request.user,
            patient=patient,
            service=f"Lab Test",
            unit='pathology',
            price=total_amount,
            status=False
        )
        LabTesting.objects.filter(labtest=labtest).update(payment=paypoint)

        messages.success(self.request, 'TEST REQUEST ADDED')
        return HttpResponseRedirect(self.get_success_url())

    def formset_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))

    def get_success_url(self):
        return reverse('patient_details', kwargs={'file_no': self.kwargs['file_no']})


def get_lab(request, lab_name):
    print(f"Received request for lab: {lab_name}")
    items = GenericTest.objects.filter(lab=lab_name)
    print(f"Found {items.count()} items")
    item_list = [{
        'id': item.id,
        'name': item.name,
        'price': float(item.price) if item.price else 0.0
    } for item in items]

    if not item_list:
        return JsonResponse({'items': []}) 

    return JsonResponse({'items': item_list})


from django.db.models import Prefetch
class LabTestDetailView(DetailView):
    model = LabTest
    template_name = 'ehr/revenue/labtest_detail.html'
    context_object_name = 'tests'  # Changed to match your template

    def get_queryset(self):
        return LabTest.objects.select_related(
            'user',
            'patient',
        ).prefetch_related(
            Prefetch(
                'items',
                queryset=LabTesting.objects.select_related(
                    'item',
                    'payment'
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testing_items'] = self.object.items.all()
        
        # Get payment status from the first item as shown in your template
        first_item = self.object.items.first()
        if first_item and first_item.payment:
            context['payment_status'] = first_item.payment.status
        else:
            context['payment_status'] = False
            
        return context

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("UTF-8")), 
        result,
        encoding='UTF-8'
    )
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class TestPDFView(DetailView):
    model = LabTest
    template_name = 'ehr/revenue/test_pdf.html'
    
    def get_queryset(self):
        return LabTest.objects.select_related(
            'user',
            'patient'
        ).prefetch_related(
            Prefetch(
                'items',
                queryset=LabTesting.objects.select_related('item', 'payment')
            )
        )

    def get(self, request, *args, **kwargs):
        labtest = self.get_object()
        testing_items = labtest.items.all()
        
        # Get payment status from first item
        payment_status = False
        first_item = testing_items.first()
        if first_item and first_item.payment:
            payment_status = first_item.payment.status
        
        context = {
            'labtest': labtest,
            'testing_items': testing_items,
            'payment_status': payment_status,
            'generated_date': datetime.now().strftime('%d-%m-%Y %H:%M'),
            'doc_title': 'LABORATORY TEST REPORT',
        }
        
        pdf = render_to_pdf(self.template_name, context)
        
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            if 'download' in request.GET:
                filename = f"LAB_TEST_{labtest.patient.file_no}_{datetime.now().strftime('%Y%m%d')}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            else:
                response['Content-Disposition'] = 'inline'
            return response
            
        return HttpResponse("Error Generating PDF", status=500)


class MicrobiologyTestListView(LoginRequiredMixin, ListView):
    model = LabTesting
    template_name = 'incoming_req.html'
    context_object_name = 'tests'
    paginate_by = 50  # Adjust as needed

    def get_queryset(self):
        queryset = super().get_queryset().filter(lab__icontains='MICROBIOLOGY').select_related(
            'labtest',
            'labtest__patient',
            'labtest__user',
            'item',
            'payment'
        ).order_by('-labtest__created')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(labtest__patient__first_name__icontains=query) |
                Q(labtest__patient__last_name__icontains=query) |
                Q(labtest__patient__other_name__icontains=query) |
                Q(labtest__patient__file_no__icontains=query)|
                Q(labtest__patient__phone__icontains=query)|
                Q(labtest__patient__title__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lab_name'] = 'MICROBIOLOGY'
        context['dashboard_url'] = 'results:micro'
        context['query'] = self.request.GET.get('q', '')       
        return context


class ChempathTestListView(LoginRequiredMixin, ListView):
    model = LabTesting
    template_name = 'incoming_req.html'
    context_object_name = 'tests'
    paginate_by = 50  # Adjust as needed

    def get_queryset(self):
        queryset = super().get_queryset().filter(lab__icontains='CHEMICAL PATHOLOGY').select_related(
            'labtest',
            'labtest__patient',
            'labtest__user',
            'item',
            'payment'
        ).order_by('-labtest__created')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(labtest__patient__first_name__icontains=query) |
                Q(labtest__patient__last_name__icontains=query) |
                Q(labtest__patient__other_name__icontains=query) |
                Q(labtest__patient__file_no__icontains=query)|
                Q(labtest__patient__phone__icontains=query)|
                Q(labtest__patient__title__icontains=query)
            )
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lab_name'] = 'CHEMICAL PATHOLOGY'
        context['dashboard_url'] = 'results:chempath'
        context['query'] = self.request.GET.get('q', '')       
        return context
    
class HematologyTestListView(LoginRequiredMixin, ListView):
    model = LabTesting
    template_name = 'incoming_req.html'
    context_object_name = 'tests'
    paginate_by = 50  # Adjust as needed

    def get_queryset(self):
        queryset = super().get_queryset().filter(lab__icontains='HEMATOLOGY').select_related(
            'labtest',
            'labtest__patient',
            'labtest__user',
            'item',
            'payment'
        ).order_by('-labtest__created')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(labtest__patient__first_name__icontains=query) |
                Q(labtest__patient__last_name__icontains=query) |
                Q(labtest__patient__other_name__icontains=query) |
                Q(labtest__patient__file_no__icontains=query)|
                Q(labtest__patient__phone__icontains=query)|
                Q(labtest__patient__title__icontains=query)
            )
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lab_name'] = 'HEMATOLOGY'
        context['dashboard_url'] = 'results:hematology'
        context['query'] = self.request.GET.get('q', '')       
        return context

class SerologyTestListView(LoginRequiredMixin, ListView):
    model = LabTesting
    template_name = 'incoming_req.html'
    context_object_name = 'tests'
    paginate_by = 50  # Adjust as needed

    def get_queryset(self):
        queryset = super().get_queryset().filter(lab__icontains='SEROLOGY').select_related(
            'labtest',
            'labtest__patient',
            'labtest__user',
            'item',
            'payment'
        ).order_by('-labtest__created')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(labtest__patient__first_name__icontains=query) |
                Q(labtest__patient__last_name__icontains=query) |
                Q(labtest__patient__other_name__icontains=query) |
                Q(labtest__patient__file_no__icontains=query)|
                Q(labtest__patient__phone__icontains=query)|
                Q(labtest__patient__title__icontains=query)
            )
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lab_name'] = 'SEROLOGY'
        context['dashboard_url'] = 'results:serology'
        context['query'] = self.request.GET.get('q', '')       
        return context