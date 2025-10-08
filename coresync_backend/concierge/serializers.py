"""Serializers for Concierge app."""
from rest_framework import serializers
from .models import ConciergeRequest


class ConciergeRequestListSerializer(serializers.ModelSerializer):
    """List view of concierge requests."""
    
    customer_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    can_cancel = serializers.SerializerMethodField()
    is_within_budget = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ConciergeRequest
        fields = [
            'id', 'request_number', 'customer_name',
            'request_type', 'request_type_display',
            'title', 'status', 'status_display',
            'budget_min', 'budget_max', 'actual_cost',
            'is_within_budget', 'preferred_pickup_date',
            'submitted_at', 'can_cancel'
        ]
    
    def get_can_cancel(self, obj):
        return obj.can_be_cancelled


class ConciergeRequestDetailSerializer(serializers.ModelSerializer):
    """Full details of a concierge request."""
    
    customer_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    can_cancel = serializers.SerializerMethodField()
    can_approve = serializers.SerializerMethodField()
    is_within_budget = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ConciergeRequest
        fields = [
            'id', 'request_number', 'customer_name',
            'request_type', 'request_type_display',
            'title', 'description', 'product_link',
            'status', 'status_display',
            'budget_min', 'budget_max', 'actual_cost',
            'is_within_budget',
            'preferred_pickup_date', 'pickup_booking',
            'submitted_at', 'reviewed_at', 'completed_at',
            'requires_age_verification', 'age_verified',
            'attachments', 'decline_reason',
            'paid_at', 'can_cancel', 'can_approve'
        ]
    
    def get_can_cancel(self, obj):
        return obj.can_be_cancelled
    
    def get_can_approve(self, obj):
        return obj.can_be_approved


class CreateConciergeRequestSerializer(serializers.Serializer):
    """Serializer for creating new concierge requests."""
    
    request_type = serializers.ChoiceField(choices=ConciergeRequest.REQUEST_TYPES)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    product_link = serializers.URLField(required=False, allow_blank=True)
    budget_min = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    budget_max = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    preferred_pickup_date = serializers.DateField()
    attachments = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    
    def validate(self, data):
        """Validate that max budget >= min budget"""
        if data['budget_min'] > data['budget_max']:
            raise serializers.ValidationError({
                'budget_max': 'Maximum budget must be greater than or equal to minimum budget'
            })
        return data

