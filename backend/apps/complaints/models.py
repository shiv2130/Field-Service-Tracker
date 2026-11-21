from django.db import models
from django.conf import settings
from apps.service_site.models import Site


class Complaint(models.Model):

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('raised', 'Raised'),
        ('assigned', 'Assigned'),
        ('on_the_way', 'On The Way'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
        ('closed_no_otp', 'Closed Without OTP'),
    ]

    ticket_no = models.CharField(max_length=20, unique=True)

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='complaints'
    )

    issue_type = models.CharField(max_length=100)
    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='raised'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )

    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='raised_complaints'
    )

    contact_phone = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ticket_no

class ClosureOTP(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='closure_otps'
    )
    otp_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP - {self.complaint.ticket_no}"

class StatusEvent(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='status_events'
    )
    old_status = models.CharField(max_length=30)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.ticket_no}: {self.old_status} -> {self.new_status}"