from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r"books", api_views.BookViewSet, basename="book")
router.register(r"members", api_views.MemberViewSet, basename="member")

urlpatterns = [
    path("", include(router.urls)),
]
