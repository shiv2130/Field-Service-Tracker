from rest_framework import serializers
from .models import Complaint, StatusEvent


class StatusEventSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(
        source='changed_by.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = StatusEvent
        fields = [
            'old_status',
            'new_status',
            'changed_by_name',
            'remarks',
            'created_at'
        ]

class ComplaintSerializer(serializers.ModelSerializer):
    site_address = serializers.CharField(
        source='site.address',
        read_only=True
    )

    customer_name = serializers.CharField(
        source='site.customer.name',
        read_only=True
    )

    engineer_name = serializers.CharField(
        source='assigned_to.name',
        read_only=True,
        allow_null=True
    )

    raised_by_name = serializers.CharField(
        source='raised_by.name',
        read_only=True,
        allow_null=True
    )

    status_events = StatusEventSerializer(
    many=True,
    read_only=True
)

    class Meta:
        model = Complaint

        fields = [
            'id',
            'ticket_no',
            'site',
            'site_address',
            'customer_name',
            'issue_type',
            'description',
            'priority',
            'status',
            'assigned_to',
            'engineer_name',
            'raised_by',
            'raised_by_name',
            'contact_phone',
            'created_at',
            'status_events'
        ]

        read_only_fields = [
            'id',
            'raised_by',
            'raised_by_name',
            'contact_phone',
            'created_at',
            'engineer_name',
            'site_address',
            'customer_name',
            'status',
            'assigned_to'
        ]


class ComplaintAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Complaint
        fields = ['assigned_to']

    def validate_assigned_to(self, value):

        if value.role != 'engineer':
            raise serializers.ValidationError(
                "Complaint can only be assigned to an engineer."
            )

        if not value.is_active:
            raise serializers.ValidationError(
                "This engineer account is inactive."
            )

        return value


class ComplaintStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Complaint
        fields = ['status']

    def validate_status(self, value):

        current_status = self.instance.status

        allowed_transitions = {
            'assigned': ['on_the_way', 'in_progress'],
            'on_the_way': ['in_progress'],
            'in_progress': ['pending'],
            'pending': ['in_progress'],
        }

        if value not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}."
            )

        return value
