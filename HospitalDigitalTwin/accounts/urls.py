from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_page, name='login'),
    path('admin-login/', views.admin_login_submit, name='admin_login_submit'),
    path('patient-login/', views.patient_login_submit, name='patient_login_submit'),
    path('logout/', views.logout_view, name='logout'),
]
