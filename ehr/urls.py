from django.urls import path, include
from .views import *
from . import views

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    # path('patients/', PatientListView.as_view(), name='patient'),


    # path('report/', views.report, name='report'),

    # path('gen_report/', GenReportView.as_view(), name='gen_report'),
    # path('gen_pdf/', views.Gen_pdf, name='gen_pdf'),
    # path('gen_csvFile/', views.Gen_csv, name='gen_csv'),


    # path('stats/', StatsView.as_view(), name='stats'),
    # path('notice/', NoticeView.as_view(), name='notice'),

    # path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    # path('logout/', CustomLogoutView.as_view(), name='logout'),

    # path('profile/<str:username>/',ProfileDetailView.as_view(), name='profile_details'),
    # path('update-user/<int:pk>/', UpdateUserView.as_view(), name='update_user'),
    # path('update-profile/<int:pk>/',UpdateProfileView.as_view(), name='update_profile'),

    # path('', include('django.contrib.auth.urls')),
]
