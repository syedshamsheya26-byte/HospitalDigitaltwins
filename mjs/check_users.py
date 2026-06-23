import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.contrib.auth.models import User
users = User.objects.all()
print(f"{len(users)} user(s):")
for u in users:
    print(f"  {u.id}: {u.username} staff={u.is_staff} super={u.is_superuser} active={u.is_active}")
