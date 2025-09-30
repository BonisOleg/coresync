"""
DRF Serializers for Services app.
Clean, safe serializers without conflicts.
"""
from rest_framework import serializers
from .models import Service, ServiceCategory, ServiceAddon, ServiceHistory


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories (Mensuite, Coresync Private)"""
    
    class Meta:
        model = ServiceCategory
        fields = [
            'id', 'name', 'slug', 'description', 'image',
            'featured_technologies', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ServiceAddonSerializer(serializers.ModelSerializer):
    """Serializer for service add-ons"""
    
    class Meta:
        model = ServiceAddon
        fields = [
            'id', 'name', 'description', 'price',
            'available_for_all_services', 'is_active'
        ]
        read_only_fields = ['id']


class ServiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for service listing"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    member_discount_percentage = serializers.ReadOnlyField()
    savings_for_members = serializers.ReadOnlyField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'slug', 'short_description',
            'category_name', 'category_slug',
            'member_price', 'non_member_price',
            'member_discount_percentage', 'savings_for_members',
            'duration', 'max_capacity', 'featured',
            'main_image', 'requires_appointment', 'member_only'
        ]
        read_only_fields = ['id']


class ServiceDetailSerializer(serializers.ModelSerializer):
    """Full serializer for service details"""
    
    category = ServiceCategorySerializer(read_only=True)
    addons = ServiceAddonSerializer(many=True, read_only=True)
    member_discount_percentage = serializers.ReadOnlyField()
    savings_for_members = serializers.ReadOnlyField()
    
    def get_price_for_user(self, obj):
        """Get price based on user membership status"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_price_for_user(request.user)
        return obj.non_member_price
    
    price_for_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'member_price', 'non_member_price',
            'price_for_user', 'member_discount_percentage', 'savings_for_members',
            'duration', 'max_capacity', 'requires_appointment', 'member_only',
            'featured', 'main_image', 'gallery_images', 'video_url',
            'meta_title', 'meta_description', 'addons', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceHistorySerializer(serializers.ModelSerializer):
    """Serializer for user service history"""
    
    service = ServiceListSerializer(read_only=True)
    addons = ServiceAddonSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = ServiceHistory
        fields = [
            'id', 'service', 'service_date', 'completion_date',
            'price_paid', 'addons', 'addons_total', 'total_amount',
            'rating', 'feedback', 'payment_status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']




