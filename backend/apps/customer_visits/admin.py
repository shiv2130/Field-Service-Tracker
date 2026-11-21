from django.contrib import admin
from .models import CustomerVisit, WorkLog, VisitPhoto
# Register your models here.

@admin.register(CustomerVisit)
class CustomerVisitAdmin(admin.ModelAdmin):

    list_display = (
        'complaint',
        'engineer',
        'check_in_time',
        'is_inside_geofence',
        'check_out_time',
    )

    list_filter = ('is_inside_geofence', 'check_in_time')
    search_fields = ('complaint__ticket_no', 'engineer__username')

@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('visit', 'description', 'created_at')


@admin.register(VisitPhoto)
class VisitPhotoAdmin(admin.ModelAdmin):
    list_display = ('visit', 'caption', 'uploaded_at')