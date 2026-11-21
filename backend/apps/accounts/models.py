from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = [
        ('office', 'Office'),
        ('engineer', 'Engineer'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='office')
    REQUIRED_FIELDS = ['name', 'phone']
    def __str__(self):
        return self.name