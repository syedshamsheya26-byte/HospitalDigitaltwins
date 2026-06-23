from rest_framework import serializers
from .models import Book, Member


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ["id", "name", "email", "phone", "joined_date"]


class BookSerializer(serializers.ModelSerializer):
    borrowed_by_name = serializers.CharField(source="borrowed_by.name", read_only=True, default=None)

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "isbn",
            "available", "borrowed_by", "borrowed_by_name",
            "borrowed_date",
        ]
