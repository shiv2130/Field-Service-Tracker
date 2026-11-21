from django.contrib import admin
from .models import Site
# Register your models here.

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address', 'contact_name', 'contact_phone')
    search_fields = ('address', 'contact_name', 'customer__name')