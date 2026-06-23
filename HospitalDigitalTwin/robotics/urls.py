from django.urls import path
from . import views

app_name = 'robotics'

urlpatterns = [
    path('', views.robot_list, name='robot_list'),
    path('create/', views.robot_create, name='robot_create'),
    path('<int:pk>/', views.robot_detail, name='robot_detail'),
    path('<int:pk>/update/', views.robot_update, name='robot_update'),
    path('procedures/', views.procedure_list, name='procedure_list'),
    path('procedures/create/', views.procedure_create, name='procedure_create'),
]
