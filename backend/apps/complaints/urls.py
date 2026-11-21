from django.urls import path
from .views import ComplaintListCreateView, ComplaintAssignmentView, ComplaintStatusUpdateView, GenerateClosureOTPView, VerifyClosureOTPView, ManagerComplaintListView, RequestClosureWithoutOTPView, ManagerPendingClosureListView, ManagerApproveClosureView

urlpatterns = [
    path('', ComplaintListCreateView.as_view(), name='complaint-list-create'),
    path(
        '<int:pk>/assign/',
        ComplaintAssignmentView.as_view(),
        name='complaint-assign'
    ),
    path(
    '<int:pk>/status/',
    ComplaintStatusUpdateView.as_view(),
    name='complaint-status-update'
    ),

    path(
    '<int:pk>/generate-otp/',
    GenerateClosureOTPView.as_view(),
    name='generate-closure-otp'
    ),

    path(
    '<int:pk>/verify-otp/',
    VerifyClosureOTPView.as_view(),
    name='verify-closure-otp'
    ),
    path(
    'manager/complaints/',
    ManagerComplaintListView.as_view(),
    name='manager-complaints'
 ),
   path(
    '<int:pk>/request-closure-no-otp/',
    RequestClosureWithoutOTPView.as_view(),
    name='request-closure-no-otp'
 ),
 path(
    'manager/pending-closures/',
    ManagerPendingClosureListView.as_view(),
    name='manager-pending-closures'
),
path(
    '<int:pk>/approve-closure/',
    ManagerApproveClosureView.as_view(),
    name='approve-closure'
),
]
