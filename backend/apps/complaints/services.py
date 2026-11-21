import secrets
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.hashers import make_password

from .models import ClosureOTP, StatusEvent


def generate_closure_otp(complaint):
    otp = str(secrets.randbelow(900000)+ 100000)

    otp_record = ClosureOTP.objects.create(
        complaint=complaint,
        otp_hash=make_password(otp),
        expires_at=timezone.now() + timedelta(minutes=5)
    )

    return otp, otp_record


def record_status_event(complaint, old_status, new_status, user, remarks=""):
    StatusEvent.objects.create(
        complaint=complaint,
        old_status=old_status,
        new_status=new_status,
        changed_by=user,
        remarks=remarks
    )