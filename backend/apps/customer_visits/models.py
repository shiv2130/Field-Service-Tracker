from django.db import models
from django.conf import settings
from apps.complaints.models import Complaint
# Create your models here.


class CustomerVisit(models.Model):

    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='visits'
    )

    engineer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_visits'
    )

    # Engineer's GPS coordinates at check-in
    check_in_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    check_in_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    # Server-generated check-in time
    check_in_time = models.DateTimeField(auto_now_add=True)

    # Geofence verification
    distance_from_site = models.FloatField(null=True, blank=True)

    is_inside_geofence = models.BooleanField(default=False)

    # Check-out information
    check_out_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    check_out_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    check_out_time = models.DateTimeField(
        null=True,
        blank=True
    )

    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.complaint.ticket_no} - {self.engineer.username}"


class WorkLog(models.Model):
    visit = models.ForeignKey(
        CustomerVisit,
        on_delete=models.CASCADE,
        related_name='work_logs'
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Work log - {self.visit.complaint.ticket_no}"

class VisitPhoto(models.Model):
    visit = models.ForeignKey(
        CustomerVisit,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    image = models.ImageField(upload_to='visit_photos/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo - {self.visit.complaint.ticket_no}"