# Create your models here.
from django.db import models
from apps.customer.models import Customer


class Site(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='sites'
    )

    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    geofence_meters = models.PositiveIntegerField(default=100)

    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.customer.name} - {self.address}"