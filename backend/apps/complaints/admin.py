
from django.contrib import admin
from .models import Complaint, ClosureOTP, StatusEvent


# Complaint Admin
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = (
        'ticket_no',
        'site',
        'issue_type',
        'priority',
        'status',
        'assigned_to',
        'raised_by',
        'created_at'
    )

    list_filter = (
        'priority',
        'status',
        'created_at'
    )

    search_fields = (
        'ticket_no',
        'issue_type',
        'description',
        'site__address',
        'assigned_to__username'
    )

    readonly_fields = (
        'created_at',
        'raised_by',
        'contact_phone',
        'status',
        'assigned_to'
    )

    list_select_related = (
        'site',
        'assigned_to',
        'raised_by'
    )

    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


# Closure OTP Admin
@admin.register(ClosureOTP)
class ClosureOTPAdmin(admin.ModelAdmin):

    list_display = (
        'complaint',
        'created_at',
        'expires_at',
        'verified_at',
        'attempts',
        'is_used'
    )

    list_filter = (
        'is_used',
        'created_at',
        'expires_at'
    )

    search_fields = (
        'complaint__ticket_no',
    )

    readonly_fields = (
        'complaint',
        'otp_hash',
        'created_at',
        'expires_at',
        'verified_at',
        'attempts',
        'is_used'
    )

    def has_add_permission(self, request):
        return False


# Complaint Status History Admin
@admin.register(StatusEvent)
class StatusEventAdmin(admin.ModelAdmin):

    list_display = (
        'complaint',
        'old_status',
        'new_status',
        'changed_by',
        'created_at'
    )

    list_filter = (
        'old_status',
        'new_status',
        'created_at'
    )

    search_fields = (
        'complaint__ticket_no',
        'changed_by__username'
    )

    readonly_fields = (
        'complaint',
        'old_status',
        'new_status',
        'changed_by',
        'remarks',
        'created_at'
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
