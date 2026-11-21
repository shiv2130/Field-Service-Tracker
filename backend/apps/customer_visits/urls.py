from django.urls import path
from .views import CustomerCheckInView, CustomerCheckOutView, WorkLogCreateView, VisitPhotoUploadView, GeofenceViolationListView, ManagerVisitListView

urlpatterns = [
    path('check-in/', CustomerCheckInView.as_view(), name='customer-check-in'),
    path(
        '<int:pk>/check-out/',
        CustomerCheckOutView.as_view(),
        name='customer-check-out'
    ),
    path('work-logs/', WorkLogCreateView.as_view(), name='work-log-create'),
    path('photos/', VisitPhotoUploadView.as_view(), name='visit-photo-upload'),
    path(
    'manager/geofence-violations/',
    GeofenceViolationListView.as_view(),
    name='geofence-violations'
    ) ,
    path(
    'manager/visits/',
    ManagerVisitListView.as_view(),
    name='manager-visits'
   ),
]