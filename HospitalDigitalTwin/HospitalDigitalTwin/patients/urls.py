from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('create/', views.patient_create, name='patient_create'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/update/', views.patient_update, name='patient_update'),
    path('<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('<int:pk>/add_medical_history/', views.add_medical_history, name='add_medical_history'),
    path('<int:pk>/add_food_history/', views.add_food_history, name='add_food_history'),
    path('sessions/', views.patient_session_list, name='patient_session_list'),
]
