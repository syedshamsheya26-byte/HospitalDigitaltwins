import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.test import Client
c = Client()
response = c.post("/admin/login/", {"username": "zainu", "password": "siya", "next": "/admin/"})
print("Status:", response.status_code)
print("Redirects:", response.redirect_chain if hasattr(response, "redirect_chain") else [])
if response.status_code == 200:
    if "Please enter the correct username" in response.content.decode():
        print("LOGIN FAILED - wrong credentials")
    else:
        print("Page loaded but no redirect. Check content.")
else:
    print("LOGIN SUCCESS (redirect)")
