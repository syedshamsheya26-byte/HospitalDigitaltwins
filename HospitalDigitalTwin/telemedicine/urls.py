from django.urls import path
from . import views

app_name = 'telemedicine'

urlpatterns = [
    path('', views.session_list, name='session_list'),
    path('create/', views.session_create, name='session_create'),
    path('<int:pk>/', views.session_detail, name='session_detail'),
    path('<int:pk>/update/', views.session_update, name='session_update'),
]
