from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'name', 'phone', 'role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('name', 'phone', 'role')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('name', 'phone', 'role')
        }),
    )
admin.site.register(User, CustomUserAdmin)