# suplay_app/supplies/models.py

from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    def __str__(self): return self.name

class Product(models.Model):
    # ... existing fields ...
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    # ... other fields ...
