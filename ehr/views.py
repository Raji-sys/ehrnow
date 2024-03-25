from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, ListView
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from .models import *
from .forms import *
from .filters import *
from django.contrib.auth import get_user_model
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime
from django.conf import settings
import os
import csv
from django.db.models import Count
User = get_user_model()


def log_anonymous_required(view_function, redirect_to=None):
    if redirect_to is None:
        redirect_to = '/'
    return user_passes_test(lambda u: not u.is_authenticated, login_url=redirect_to)(view_function)


# @login_required
# def fetch_resources(uri, rel):
#     """
#     Handles fetching static and media resources when generating the PDF.
#     """
#     if uri.startswith(settings.STATIC_URL):
#         path = os.path.join(settings.STATIC_ROOT,
#                             uri.replace(settings.STATIC_URL, ""))
#     else:
#         path = os.path.join(settings.MEDIA_ROOT,
#                             uri.replace(settings.MEDIA_URL, ""))
#     return path


# @method_decorator(login_required(login_url='login'), name='dispatch')
class IndexView(TemplateView):
    template_name = "index.html"


class GetStartedView(TemplateView):
    template_name = "get_started.html"

@method_decorator(log_anonymous_required, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'get_started.html'

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy('index')
        else:
            pass
            # return reverse_lazy('profile_details', args=[self.request.user.username])


# @method_decorator(login_required(login_url='login'), name='dispatch')
# class CustomLogoutView(LogoutView):
#     template_name = 'login.html'

#     def dispatch(self, request, *args, **kwargs):
#         response = super().dispatch(request, *args, **kwargs)
#         messages.success(request, 'logout successful')
#         return response


def reg_anonymous_required(view_function, redirect_to=None):
    if redirect_to is None:
        redirect_to = '/'
    return user_passes_test(lambda u: not u.is_authenticated or u.is_superuser, login_url=redirect_to)(view_function)


# @method_decorator(reg_anonymous_required, name='dispatch')
# class UserRegistrationView(CreateView):
#     form_class = CustomUserCreationForm
#     template_name = 'registration/register.html'
#     success_url = ""

#     def form_valid(self, form):
#         if form.is_valid():
#             response = super().form_valid(form)
#             user = User.objects.get(username=form.cleaned_data['username'])
#             profile_instance = Profile(user=user)
#             profile_instance.save()
#             # govapp_instance = GovernmentAppointment(user=user)
#             # govapp_instance.save()
#             messages.success(
#                 self.request, f"Registration for: {user.get_full_name()} was successful")
#             return response
#         else:
#             print("Form errors:", form.errors)
#             return self.form_invalid(form)

#     def get_success_url(self):
#         if self.request.user.is_superuser:
#             pass
#             # return reverse_lazy('patient')
#         else:
#             return reverse_lazy('index')


# @method_decorator(login_required(login_url='login'), name='dispatch')
# class UpdateUserView(UpdateView):
#     model = User
#     template_name = 'patient/update-user.html'
#     form_class = UserForm
#     success_url = reverse_lazy('profile_details')

#     def get_success_url(self):
#         messages.success(
#             self.request, 'patient Information Updated Successfully')
#         return reverse_lazy('profile_details', kwargs={'username': self.object.username})

#     def form_valid(self, form):
#         if form.is_valid():
#             form.save()
#             return super().form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, 'error updating patient information')
#         return self.render_to_response(self.get_context_data(form=form))


# @method_decorator(login_required(login_url='login'), name='dispatch')
# class UpdateProfileView(UpdateView):
#     model = Profile
#     template_name = 'patient/update-profile.html'
#     form_class = ProfileForm
#     success_url = reverse_lazy('profile_details')

#     def get_success_url(self):
#         messages.success(
#             self.request, 'patient Information Updated Successfully')
#         return reverse_lazy('profile_details', kwargs={'username': self.object.user})

#     def form_valid(self, form):
#         if form.is_valid():
#             form.save()
#             return super().form_valid(form)
#         else:
#             return self.form_invalid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, 'error updating patient information')
#         return self.render_to_response(self.get_context_data(form=form))


# @method_decorator(login_required(login_url='login'), name='dispatch')
# class ProfileDetailView(DetailView):
#     template_name = 'patient/profile_details.html'
#     model = Profile

#     def get_object(self, queryset=None):
#         if self.request.user.is_superuser:
#             username_from_url = self.kwargs.get('username')
#             user = get_object_or_404(User, username=username_from_url)
#         else:
#             user = self.request.user
#         return get_object_or_404(Profile, user=user)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         profile = context['object']

#         qualifications = Qualification.objects.filter(user=profile.user)

#         context['qualifications'] = qualifications
#         context['Qualform'] = QualForm()
#         return context