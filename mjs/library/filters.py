import django_filters
from django.db.models import Q
from .models import Book


class BookFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(lookup_expr="icontains")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Book
        fields = ["available", "author", "search"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value)
            | Q(author__icontains=value)
            | Q(isbn__icontains=value)
        )
