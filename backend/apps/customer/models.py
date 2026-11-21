from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=150)
    billing_address = models.TextField(blank=True)
    billing_email = models.EmailField(blank=True)
    billing_phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
