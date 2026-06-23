from datetime import date

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend

from .models import Book, Member
from .serializers import BookSerializer, MemberSerializer
from .filters import BookFilter


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("borrowed_by").all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ["title", "author", "isbn"]
    ordering_fields = ["title", "author"]
    ordering = ["title"]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    @action(detail=True, methods=["post"])
    def issue(self, request, pk=None):
        book = self.get_object()
        member_id = request.data.get("member_id")
        if not member_id:
            return Response({"error": "member_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not book.available:
            return Response({"error": "Book is already issued"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            member = Member.objects.get(pk=member_id)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        book.available = False
        book.borrowed_by = member
        book.borrowed_date = date.today()
        book.save()
        serializer = self.get_serializer(book)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        book = self.get_object()
        if book.available:
            return Response({"error": "Book is not currently issued"}, status=status.HTTP_400_BAD_REQUEST)
        book.available = True
        book.borrowed_by = None
        book.borrowed_date = None
        book.save()
        serializer = self.get_serializer(book)
        return Response(serializer.data)


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "email", "phone"]
    ordering_fields = ["name", "joined_date"]
    ordering = ["name"]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
