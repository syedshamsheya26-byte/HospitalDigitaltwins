from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('patients/', include('patients.urls')),
    path('appointments/', include('appointments.urls')),
    path('beds/', include('beds.urls')),
    path('inventory/', include('inventory.urls')),
    path('analytics/', include('analytics.urls')),
    path('predictions/', include('predictions.urls')),
    path('disease-risk/', include('disease_risk.urls')),
    path('reports/', include('reports.urls')),
    path('telemedicine/', include('telemedicine.urls')),
    path('robotics/', include('robotics.urls')),
    path('dashboard/', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
