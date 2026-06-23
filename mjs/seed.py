import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from library.models import Book, Member
from datetime import date, timedelta

members_data = [
    {"name": "Asha Sharma", "email": "asha@library.com", "phone": "9876543210"},
    {"name": "Vikram Reddy", "email": "vikram@library.com", "phone": "9876543211"},
    {"name": "Riya Gupta", "email": "riya@library.com", "phone": "9876543212"},
    {"name": "Karan Singh", "email": "karan@library.com", "phone": "9876543213"},
    {"name": "Priya Patel", "email": "priya@library.com", "phone": "9876543214"},
]

books_data = [
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "9780743273565"},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "9780061120084"},
    {"title": "1984", "author": "George Orwell", "isbn": "9780451524935"},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "9780141439518"},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "isbn": "9780316769488"},
    {"title": "One Hundred Years of Solitude", "author": "Gabriel Garcia Marquez", "isbn": "9780060883287"},
    {"title": "Brave New World", "author": "Aldous Huxley", "isbn": "9780060850524"},
    {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "isbn": "9780544003415"},
    {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "isbn": "9780439708180"},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "isbn": "9780547928227"},
    {"title": "Fahrenheit 451", "author": "Ray Bradbury", "isbn": "9781451673319"},
    {"title": "The Alchemist", "author": "Paulo Coelho", "isbn": "9780062315007"},
]

for m in members_data:
    Member.objects.get_or_create(email=m["email"], defaults=m)

for b in books_data:
    Book.objects.get_or_create(isbn=b["isbn"], defaults=b)

# Issue a couple to make it realistic
members = list(Member.objects.all())
books = list(Book.objects.all()[:3])
for i, book in enumerate(books):
    book.available = False
    book.borrowed_by = members[i % len(members)]
    book.borrowed_date = date.today() - timedelta(days=7 * (i + 1))
    book.save()

print(f"Seeded {Member.objects.count()} members and {Book.objects.count()} books")
