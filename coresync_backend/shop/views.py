"""Views for Shop app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Product, PickupOrder, OrderItem
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    PickupOrderListSerializer,
    PickupOrderDetailSerializer,
    CreatePickupOrderSerializer
)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for products (read-only for customers)."""
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        """Get products with filtering."""
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(short_description__icontains=search)
            )
        
        return queryset.order_by('category', 'name')
    
    @method_decorator(cache_page(60 * 15))  # Cache 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all product categories with counts."""
        from django.db.models import Count
        
        categories = Product.objects.filter(
            is_active=True
        ).values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        return Response({
            'categories': [
                {
                    'value': cat['category'],
                    'label': dict(Product.CATEGORIES)[cat['category']],
                    'count': cat['count']
                }
                for cat in categories
            ]
        })


class PickupOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for pickup orders."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePickupOrderSerializer
        elif self.action == 'retrieve':
            return PickupOrderDetailSerializer
        return PickupOrderListSerializer
    
    def get_queryset(self):
        """Get user's orders with optimization - PERFORMANCE FIX"""
        return PickupOrder.objects.filter(
            user=self.request.user
        ).select_related(  # Reduce N+1 queries
            'user',
            'payment',
            'pickup_booking'
        ).prefetch_related(  # Optimize items loading
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product')
            )
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create new pickup order."""
        serializer = CreatePickupOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        items_data = data.get('items', [])
        
        if not items_data:
            return Response(
                {'error': 'No items provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create order
            order = PickupOrder.objects.create(
                user=request.user,
                customer_notes=data.get('customer_notes', ''),
                pickup_date=data.get('pickup_date')
            )
            
            # Add items
            subtotal = 0
            for item_data in items_data:
                try:
                    product = Product.objects.get(
                        id=item_data['product_id'],
                        is_active=True
                    )
                except Product.DoesNotExist:
                    order.delete()
                    return Response(
                        {'error': f"Product {item_data['product_id']} not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Check stock
                if product.stock < item_data['quantity']:
                    order.delete()
                    return Response(
                        {'error': f"Insufficient stock for {product.name}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Determine price (member vs non-member)
                if hasattr(request.user, 'membership') and request.user.membership.is_active:
                    unit_price = product.member_price
                else:
                    unit_price = product.price
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    unit_price=unit_price,
                    notes=item_data.get('notes', '')
                )
                
                subtotal += unit_price * item_data['quantity']
                
                # Decrease stock
                product.stock -= item_data['quantity']
                product.save()
            
            # Calculate totals
            tax = subtotal * 0.08  # 8% tax (adjust as needed)
            order.subtotal = subtotal
            order.tax = tax
            order.total = subtotal + tax
            order.save()
            
            # Return created order
            serializer = PickupOrderDetailSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'Error creating order: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        """Cancel pickup order."""
        order = self.get_object()
        
        if not order.can_be_cancelled:
            return Response(
                {'error': 'Order cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Restore stock
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()
        
        # Cancel order
        order.status = 'cancelled'
        order.save()
        
        return Response({
            'message': 'Order cancelled successfully',
            'order_number': order.order_number
        })
