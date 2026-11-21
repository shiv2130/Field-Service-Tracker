from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from apps.complaints.services import record_status_event
from .models import CustomerVisit
from .serializers import CustomerVisitSerializer, CustomerVisitCheckOutSerializer, WorkLogSerializer, VisitPhotoSerializer
from .services import calculate_distance
from apps.accounts.permissions import IsManager

class CustomerCheckInView(generics.CreateAPIView):

    serializer_class = CustomerVisitSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        complaint = serializer.validated_data['complaint']
        engineer = request.user

        # Only assigned engineers can check in
        if engineer.role != 'engineer':
            return Response(
                {"error": "Only engineers can check in."},
                status=status.HTTP_403_FORBIDDEN
            )

        if complaint.assigned_to != engineer:
            return Response(
                {"error": "You are not assigned to this complaint."},
                status=status.HTTP_403_FORBIDDEN
            )

        if complaint.status not in ['assigned', 'on_the_way']:
            return Response(
                {"error": "Complaint is not ready for check-in."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent multiple open visits for the same complaint
        existing_visit = CustomerVisit.objects.filter(
            complaint=complaint,
            check_out_time__isnull=True
        ).exists()

        if existing_visit:
            return Response(
                {"error": "An active visit already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get engineer's GPS coordinates
        latitude = serializer.validated_data['check_in_latitude']
        longitude = serializer.validated_data['check_in_longitude']

        # Get registered customer site coordinates
        site = complaint.site

        distance = calculate_distance(
            latitude,
            longitude,
            site.latitude,
            site.longitude
        )

        inside_geofence = distance <= site.geofence_meters

        # Save visit with server-calculated values
        visit = serializer.save(
            engineer=engineer,
            distance_from_site=distance,
            is_inside_geofence=inside_geofence
        )

        # Update complaint status
        old_status = complaint.status

        complaint.status = 'in_progress'
        complaint.save(update_fields=['status'])

        # Record status change
        record_status_event(
            complaint=complaint,
            old_status=old_status,
            new_status='in_progress',
            user=request.user,
            remarks="Engineer checked in at customer site."
        )

        return Response(
            CustomerVisitSerializer(visit).data,
            status=status.HTTP_201_CREATED
        )

class CustomerCheckOutView(generics.UpdateAPIView):
    serializer_class = CustomerVisitCheckOutSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerVisit.objects.filter(
            engineer = self.request.user,
            check_out_time__isnull =True
        )
    def update(self, request, *args, **kwargs):
        visit = self.get_object()
        serializer = self.get_serializer(
            visit,
            data = request.data
        )
        serializer.is_valid(raise_exception = True)
        check_out_time = timezone.now()
        duration = check_out_time - visit.check_in_time

        duration_minutes = max(
            0, 
            int(duration.total_seconds() // 60)
        )

        serializer.save(
            check_out_time=check_out_time,
            duration_minutes = duration_minutes
        )

        return Response(
            {
                "message": "Check-out sucessful.",
                "visit_id": visit.id, 
                "check_in_time": visit.check_in_time,
                "check_out_time": visit.check_out_time,
                "duration_minutes": visit.duration_minutes,
                "check_out_latitude": visit.check_out_latitude,
                "check_out_longitude": visit.check_out_longitude
            },
            status = status.HTTP_200_OK
        )


class WorkLogCreateView(generics.CreateAPIView):
    serializer_class = WorkLogSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        visit = serializer.validated_data['visit']
        if visit.engineer != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You are not authorized to add a work log to this visit."
            )
        
        if visit.check_out_time is not None:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                "Cannot add a work log to a completed visit."
            )

        serializer.save()


class VisitPhotoUploadView(generics.CreateAPIView):
    serializer_class = VisitPhotoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        visit = serializer.validated_data['visit']

        if visit.engineer != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You are not authorized to upload photos for this visit."
            )

        if visit.check_out_time is not None:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                "Cannot upload photos to a completed visit."
            )

        serializer.save()

class GeofenceViolationListView(generics.ListAPIView):

    serializer_class = CustomerVisitSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):
        return CustomerVisit.objects.filter(
            is_inside_geofence=False
        ).select_related(
            'complaint',
            'engineer',
            'complaint__site'
        ).order_by('-check_in_time')

class ManagerVisitListView(generics.ListAPIView):
    serializer_class = CustomerVisitSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):
        return CustomerVisit.objects.select_related(
            'complaint',
            'engineer',
            'complaint__site'
        ).order_by('-check_in_time')