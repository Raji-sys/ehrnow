from django.urls import path, include
from .views import *
from django.urls import path
from . import views

app_name='page'

urlpatterns = [
    path('site/', IndexView.as_view(), name='portofolio_index'), 
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('blog/', views.blog, name='blog'),
    path('resume/', views.resume, name='resume'),
    path('contact/', views.contact, name='contact'),
    path('',include('django.contrib.auth.urls')),
    path('submit-testimonial/', TestimonialCreateView.as_view(), name='submit_testimonial'),
    path('contact-form/', ContactMessageCreateView.as_view(), name='contact_us'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
]
