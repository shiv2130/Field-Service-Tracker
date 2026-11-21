from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from apps.complaints.services import generate_closure_otp
from .models import Complaint, ClosureOTP
from .serializers import ComplaintSerializer, ComplaintAssignmentSerializer, ComplaintStatusSerializer
from apps.accounts.permissions import IsOfficeOrManager
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from .services import record_status_event
from apps.accounts.permissions import IsManager



class ComplaintListCreateView(generics.ListCreateAPIView):

    serializer_class = ComplaintSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == 'engineer':
            return Complaint.objects.filter(assigned_to=user)

        if user.role in ['office', 'manager', 'admin']:
            return Complaint.objects.all()

        return Complaint.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsOfficeOrManager()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            raised_by=self.request.user,
            contact_phone=serializer.validated_data['site'].contact_phone
        )



class ComplaintAssignmentView(generics.UpdateAPIView):

    queryset = Complaint.objects.all()
    serializer_class = ComplaintAssignmentSerializer
    permission_classes = [IsOfficeOrManager]

    def update(self, request, *args, **kwargs):

        complaint = self.get_object()
        old_status = complaint.status

        serializer = self.get_serializer(
            complaint,
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(status='assigned')

        new_status = complaint.status

        record_status_event(
            complaint=complaint,
            old_status=old_status,
            new_status=new_status,
            user=request.user,
            remarks="Complaint assigned to engineer."
        )

        return Response(
            ComplaintSerializer(complaint).data,
            status=status.HTTP_200_OK
        )


class ComplaintStatusUpdateView(generics.UpdateAPIView):

    serializer_class = ComplaintStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'engineer':
            return Complaint.objects.filter(assigned_to=user)

        return Complaint.objects.none()

    def update(self, request, *args, **kwargs):

        complaint = self.get_object()
        old_status = complaint.status

        serializer = self.get_serializer(
            complaint,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        new_status = complaint.status

        if old_status != new_status:
            record_status_event(
                complaint=complaint,
                old_status=old_status,
                new_status=new_status,
                user=request.user,
                remarks="Complaint status updated by engineer."
            )

        return Response(
            ComplaintSerializer(complaint).data,
            status=status.HTTP_200_OK
        )


class GenerateClosureOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)

        if request.user.role != 'engineer':
            raise PermissionDenied(
                "Only engineers can generate closure OTPs."
            )

        if complaint.assigned_to != request.user:
            raise PermissionDenied(
                "You are not assigned to this complaint."
            )

        if complaint.status != 'in_progress':
            return Response(
                {"error": "Complaint must be in progress."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp, otp_record = generate_closure_otp(complaint)

        return Response({
            "message": "Closure OTP generated successfully.",
            "complaint_id": complaint.id,
            "otp": otp,
            "expires_at": otp_record.expires_at
        }, status=status.HTTP_201_CREATED)

class VerifyClosureOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)

        if request.user.role != 'engineer':
            raise PermissionDenied(
                "Only engineers can verify closure OTPs."
            )

        if complaint.assigned_to != request.user:
            raise PermissionDenied(
                "You are not assigned to this complaint."
            )

        if complaint.status != 'in_progress':
            return Response(
                {"error": "Complaint must be in progress."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if complaint.visits.filter(
            check_out_time__isnull=True
        ).exists():
            return Response(
                {"error": "Please check out before closing the complaint."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp = request.data.get('otp')

        if not otp or not str(otp).isdigit() or len(str(otp)) != 6:
            return Response(
                {"error": "Please enter a valid 6-digit OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_record = ClosureOTP.objects.filter(
            complaint=complaint,
            is_used=False
        ).order_by('-created_at').first()

        if not otp_record:
            return Response(
                {"error": "No active OTP found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > otp_record.expires_at:
            otp_record.is_used = True
            otp_record.save(update_fields=['is_used'])

            return Response(
                {"error": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_record.attempts >= 5:
            otp_record.is_used = True
            otp_record.save(update_fields=['is_used'])

            return Response(
                {"error": "Maximum OTP attempts exceeded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(str(otp), otp_record.otp_hash):
            otp_record.attempts += 1

            if otp_record.attempts >= 5:
                otp_record.is_used = True

            otp_record.save()

            return Response(
                {"error": "Incorrect OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_record.verified_at = timezone.now()
        otp_record.is_used = True
        otp_record.save()

        old_status = complaint.status

        complaint.status = 'closed'
        complaint.save(update_fields=['status'])

        record_status_event(
            complaint=complaint,
            old_status=old_status,
            new_status='closed',
            user=request.user,
            remarks="Complaint closed after successful customer OTP verification."
        )

        return Response({
            "message": "OTP verified. Complaint closed successfully.",
            "complaint_id": complaint.id,
            "status": complaint.status,
            "verified_at": otp_record.verified_at
        }, status=status.HTTP_200_OK)


class ManagerComplaintListView(generics.ListAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):
        return Complaint.objects.select_related(
            'site',
            'site__customer',
            'assigned_to',
            'raised_by'
        ).order_by('-created_at')


class RequestClosureWithoutOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)

        if request.user.role != 'engineer':
            raise PermissionDenied(
                "Only engineers can request closure without OTP."
            )

        if complaint.assigned_to != request.user:
            raise PermissionDenied(
                "You are not assigned to this complaint."
            )

        if complaint.status != 'in_progress':
            return Response(
                {"error": "Complaint must be in progress."},
                status=status.HTTP_400_BAD_REQUEST
            )

        visit_id = request.data.get('visit_id')
        reason = request.data.get('reason', '').strip()

        if not visit_id:
            return Response(
                {"error": "Visit ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not reason:
            return Response(
                {"error": "A closure reason is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        visit = complaint.visits.filter(
            id=visit_id,
            engineer=request.user
        ).first()

        if not visit:
            return Response(
                {"error": "Valid visit not found for this complaint."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if visit.check_out_time is None:
            return Response(
                {"error": "Please check out before requesting closure."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not visit.photos.exists():
            return Response(
                {"error": "At least one visit photo is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the closure reason as a work log.
        visit.work_logs.create(description=reason)

        old_status = complaint.status
        complaint.status = 'closed_no_otp'
        complaint.save(update_fields=['status'])

        record_status_event(
            complaint=complaint,
            old_status=old_status,
            new_status='closed_no_otp',
            user=request.user,
            remarks="Engineer requested closure without OTP."
        )

        return Response({
            "message": "Closure request submitted for manager approval.",
            "complaint_id": complaint.id,
            "visit_id": visit.id,
            "status": complaint.status
        }, status=status.HTTP_200_OK)

class ManagerPendingClosureListView(generics.ListAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):
        return Complaint.objects.filter(
            status='closed_no_otp'
        ).select_related(
            'site',
            'site__customer',
            'assigned_to',
            'raised_by'
        ).order_by('-created_at')


class ManagerApproveClosureView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)

        if complaint.status != 'closed_no_otp':
            return Response(
                {"error": "Complaint is not awaiting closure approval."},
                status=status.HTTP_400_BAD_REQUEST
            )

        decision = request.data.get('decision')

        if decision not in ['approve', 'reject']:
            return Response(
                {"error": "Decision must be approve or reject."},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = complaint.status

        if decision == 'approve':
            complaint.status = 'closed'
            remarks = "Manager approved closure without OTP."
        else:
            complaint.status = 'in_progress'
            remarks = "Manager rejected closure without OTP."

        complaint.save(update_fields=['status'])

        record_status_event(
            complaint=complaint,
            old_status=old_status,
            new_status=complaint.status,
            user=request.user,
            remarks=remarks
        )

        return Response({
            "message": f"Closure request {decision}d successfully.",
            "complaint_id": complaint.id,
            "status": complaint.status
        }, status=status.HTTP_200_OK)
