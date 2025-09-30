"""
DRF Serializers for Memberships app.
Clean, safe serializers without conflicts.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import MembershipPlan, Membership, MembershipBenefit


class MembershipBenefitSerializer(serializers.ModelSerializer):
    """Serializer for membership benefits"""
    
    class Meta:
        model = MembershipBenefit
        fields = [
            'id', 'name', 'description', 'benefit_type',
            'icon', 'value'
        ]
        read_only_fields = ['id']


class MembershipPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for membership plan listing"""
    
    monthly_price = serializers.ReadOnlyField()
    
    class Meta:
        model = MembershipPlan
        fields = [
            'id', 'name', 'slug', 'short_description',
            'price', 'monthly_price', 'duration_months',
            'discount_percentage', 'featured', 'color_scheme', 'icon',
            'mensuite_access', 'coresync_private_access',
            'iot_control_access', 'priority_booking',
            'monthly_service_credits', 'guest_passes', 'order'
        ]
        read_only_fields = ['id']


class MembershipPlanDetailSerializer(serializers.ModelSerializer):
    """Full serializer for membership plan details"""
    
    monthly_price = serializers.ReadOnlyField()
    
    def calculate_example_savings(self, obj):
        """Calculate example savings for marketing"""
        return obj.calculate_savings_example()
    
    example_savings = serializers.SerializerMethodField()
    
    class Meta:
        model = MembershipPlan
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'monthly_price', 'duration_months',
            'benefits', 'discount_percentage', 'example_savings',
            'mensuite_access', 'coresync_private_access',
            'iot_control_access', 'priority_booking',
            'monthly_service_credits', 'guest_passes',
            'featured', 'color_scheme', 'icon', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for user memberships"""
    
    plan = MembershipPlanListSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    def can_use_service_credit(self, obj):
        """Check if user can use service credit"""
        return obj.can_use_service_credit()
    
    can_use_service_credit = serializers.SerializerMethodField()
    
    class Meta:
        model = Membership
        fields = [
            'id', 'plan', 'start_date', 'end_date', 'status',
            'is_active', 'days_remaining',
            'services_used_this_month', 'guest_passes_used',
            'can_use_service_credit', 'auto_renew', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MembershipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new memberships"""
    
    plan_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Membership
        fields = ['plan_id', 'auto_renew', 'notes']
        
    def validate_plan_id(self, value):
        """Validate that the membership plan exists and is active"""
        try:
            plan = MembershipPlan.objects.get(id=value, is_active=True)
            return value
        except MembershipPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid membership plan selected.")
    
    def create(self, validated_data):
        """Create new membership with calculated dates"""
        plan_id = validated_data.pop('plan_id')
        plan = MembershipPlan.objects.get(id=plan_id)
        
        # Calculate membership dates
        start_date = timezone.now().date()
        from datetime import timedelta
        end_date = start_date + timedelta(days=plan.duration_months * 30)
        
        membership = Membership.objects.create(
            user=self.context['request'].user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            **validated_data
        )
        
        return membership


class MembershipUpgradeSerializer(serializers.Serializer):
    """Serializer for membership upgrades"""
    
    plan_id = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=50, default='stripe_card')
    
    def validate_plan_id(self, value):
        """Validate upgrade plan"""
        try:
            plan = MembershipPlan.objects.get(id=value, is_active=True)
            
            # Check if user has current membership to upgrade from
            user = self.context['request'].user
            current_membership = getattr(user, 'membership', None)
            
            if not current_membership:
                raise serializers.ValidationError("No active membership to upgrade.")
            
            if current_membership.plan.price >= plan.price:
                raise serializers.ValidationError("Cannot downgrade to a lower-tier plan.")
            
            return value
        except MembershipPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid membership plan selected.")
    
    def validate_payment_method(self, value):
        """Validate payment method"""
        allowed_methods = ['stripe_card', 'stripe_apple_pay', 'stripe_google_pay']
        if value not in allowed_methods:
            raise serializers.ValidationError(f"Payment method must be one of: {allowed_methods}")
        return value




