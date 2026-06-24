from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta

class MedicineCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Medicine categories'

    def __str__(self):
        return self.name

class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ('tablet', 'Tablet'), ('capsule', 'Capsule'), ('syrup', 'Syrup'),
        ('injection', 'Injection'), ('ointment', 'Ointment'), ('drops', 'Drops'),
        ('inhaler', 'Inhaler'), ('other', 'Other'),
    ]

    medicine_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(MedicineCategory, on_delete=models.SET_NULL, null=True)
    dosage_form = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    strength = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='medicines/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.strength})"

class Inventory(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='inventory_items')
    batch_number = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=20, default='units')
    expiry_date = models.DateField()
    manufacturing_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Inventory items'

    def is_expired(self):
        return self.expiry_date < date.today() if self.expiry_date else False

    def is_low_stock(self, threshold=10):
        return self.quantity <= threshold

    def __str__(self):
        return f"{self.medicine.name} - Batch: {self.batch_number} (Qty: {self.quantity})"

class StockAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('low_stock', 'Low Stock'), ('expiry', 'Near Expiry'),
        ('out_of_stock', 'Out of Stock'),
    ]
    STATUS_CHOICES = [('active', 'Active'), ('resolved', 'Resolved')]

    inventory_item = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.alert_type} - {self.inventory_item}"
