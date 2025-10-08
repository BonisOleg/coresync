"""Serializers for Shop app."""
from rest_framework import serializers
from .models import Product, PickupOrder, OrderItem


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists."""
    
    savings_amount = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'short_description',
            'price', 'member_price', 'savings_amount', 'discount_percentage',
            'stock', 'in_stock', 'main_image', 'is_featured'
        ]
    
    def get_savings_amount(self, obj):
        return float(obj.savings_amount)
    
    def get_discount_percentage(self, obj):
        return obj.discount_percentage
    
    def get_in_stock(self, obj):
        return obj.in_stock


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product details including gallery."""
    
    savings_amount = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_display',
            'description', 'short_description',
            'price', 'member_price', 'savings_amount', 'discount_percentage',
            'stock', 'in_stock', 'is_low_stock',
            'main_image', 'gallery_images',
            'is_featured', 'is_active',
            'meta_title', 'meta_description'
        ]
    
    def get_savings_amount(self, obj):
        return float(obj.savings_amount)
    
    def get_discount_percentage(self, obj):
        return obj.discount_percentage
    
    def get_in_stock(self, obj):
        return obj.in_stock
    
    def get_is_low_stock(self, obj):
        return obj.is_low_stock


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item with product details."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.ImageField(source='product.main_image', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_image', 'product_slug',
            'quantity', 'unit_price', 'total_price', 'notes'
        ]
        read_only_fields = ['total_price']


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items."""
    
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    notes = serializers.CharField(max_length=255, required=False, allow_blank=True)


class PickupOrderListSerializer(serializers.ModelSerializer):
    """List view of pickup orders."""
    
    customer_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = PickupOrder
        fields = [
            'id', 'order_number', 'customer_name',
            'status', 'status_display',
            'pickup_date', 'items_count',
            'subtotal', 'tax', 'total',
            'paid_at', 'created_at', 'can_cancel'
        ]
    
    def get_can_cancel(self, obj):
        return obj.can_be_cancelled


class PickupOrderDetailSerializer(serializers.ModelSerializer):
    """Full order details with items."""
    
    customer_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = PickupOrder
        fields = [
            'id', 'order_number', 'customer_name',
            'status', 'status_display',
            'pickup_date', 'pickup_booking',
            'subtotal', 'tax', 'total',
            'items', 'customer_notes',
            'paid_at', 'created_at', 'updated_at',
            'can_cancel'
        ]
    
    def get_can_cancel(self, obj):
        return obj.can_be_cancelled


class CreatePickupOrderSerializer(serializers.Serializer):
    """Serializer for creating new orders."""
    
    items = OrderItemCreateSerializer(many=True)
    customer_notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )
    pickup_date = serializers.DateField(required=False, allow_null=True)

