
from rest_framework import serializers
from .models import CustomerVisit, WorkLog, VisitPhoto



class CustomerVisitSerializer(serializers.ModelSerializer):
    engineer_name = serializers.CharField(
        source='engineer.name',
        read_only=True
    )

    class Meta:
        model = CustomerVisit
        fields = [
            'id',
            'complaint',
            'engineer',
            'engineer_name',
            'check_in_latitude',
            'check_in_longitude',
            'check_in_time',
            'distance_from_site',
            'is_inside_geofence',
            'check_out_latitude',
            'check_out_longitude',
            'check_out_time',
            'duration_minutes',
        ]

        read_only_fields = [
            'id',
            'engineer',
            'engineer_name',
            'check_in_time',
            'distance_from_site',
            'is_inside_geofence',
            'check_out_latitude',
            'check_out_longitude',
            'check_out_time',
            'duration_minutes',
        ]

    def validate_check_in_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )
        return value

    def validate_check_in_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )
        return value


class CustomerVisitCheckOutSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerVisit
        fields = [
            'check_out_latitude',
            'check_out_longitude',
        ]

    def validate_check_out_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )
        return value

    def validate_check_out_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )
        return value


class WorkLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLog
        fields = ['id', 'visit', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class VisitPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitPhoto
        fields = ['id', 'visit', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']