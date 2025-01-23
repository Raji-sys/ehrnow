from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from .models import *
from .forms import *
from .filters import *
from django.views.generic import CreateView, ListView, DetailView, UpdateView


class IndexView(TemplateView):
    template_name = "page/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'education': Education.objects.all().order_by('-year_start'),
            'fellowship': Fellowship.objects.all().order_by('-date'),
            'proqual': ProfessionalQualification.objects.all().order_by('-date'),
            'experience': Experience.objects.all().order_by('-year_start'),
            'services': Service.objects.all(),
            'surgeries': Surgery.objects.all().order_by('-date')[:4],
            'blog_posts': BlogPost.objects.all().order_by('-pub_date')[:4],
            'testimonials': Testimonial.objects.all().order_by('-pub_date')[:4],
            'surgery_count': Surgery.objects.count(),
            'blog_post_count': BlogPost.objects.count(),
            'achievements_awards': AchievementAward.objects.all(),  # Add this line
        })
        return context
    

def about(request):
    return render(request, 'page/about.html')

def services(request):
    return render(request, 'page/services.html')

def portfolio(request):
    return render(request, 'page/portfolio.html')

def blog(request):
    return render(request, 'page/blog.html')

def resume(request):
    return render(request, 'page/cv.html')

def contact(request):
    return render(request, 'page/contact.html')


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'sections/blog_detail.html'
    context_object_name = 'post'


class TestimonialCreateView(CreateView):
    model = Testimonial
    fields = ['name', 'comment']
    template_name = 'sections/submit_testimonial.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        return super().form_valid(form)
    

class ContactMessageCreateView(CreateView):
    model = Contact
    fields = ['name','email','phone', 'message']
    template_name = 'sections/contact_form.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        return super().form_valid(form)
