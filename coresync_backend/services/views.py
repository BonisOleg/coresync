"""
DRF Views for Services app.
Safe ViewSets without conflicts with existing code.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils import timezone

from .models import Service, ServiceCategory, ServiceAddon, ServiceHistory
from .serializers import (
    ServiceListSerializer,
    ServiceDetailSerializer,
    ServiceCategorySerializer,
    ServiceAddonSerializer,
    ServiceHistorySerializer
)


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for service categories (Mensuite, Coresync Private)"""
    
    queryset = ServiceCategory.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = ServiceCategorySerializer
    lookup_field = 'slug'
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for spa services"""
    
    queryset = Service.objects.filter(is_active=True).select_related('category').prefetch_related('addons')
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return ServiceListSerializer
        return ServiceDetailSerializer
    
    def get_queryset(self):
        """Filter services based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(featured=True)
        
        # Filter by member-only
        member_only = self.request.query_params.get('member_only')
        if member_only and member_only.lower() == 'true':
            queryset = queryset.filter(member_only=True)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(short_description__icontains=search)
            )
        
        return queryset.order_by('category__order', 'order', 'name')
    
    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def mensuite(self, request):
        """Get services for Mensuite category"""
        mensuite_services = self.get_queryset().filter(category__slug='mensuite')
        serializer = ServiceListSerializer(mensuite_services, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='coresync-private')
    def coresync_private(self, request):
        """Get services for Coresync Private category"""
        private_services = self.get_queryset().filter(category__slug='coresync-private')
        serializer = ServiceListSerializer(private_services, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured services"""
        featured_services = self.get_queryset().filter(featured=True)
        serializer = ServiceListSerializer(featured_services, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def addons(self, request, slug=None):
        """Get available add-ons for a specific service"""
        service = self.get_object()
        
        # Get service-specific add-ons + universal add-ons
        addons = ServiceAddon.objects.filter(
            Q(services=service) | Q(available_for_all_services=True),
            is_active=True
        ).distinct()
        
        serializer = ServiceAddonSerializer(addons, many=True)
        return Response(serializer.data)


class ServiceAddonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for service add-ons"""
    
    queryset = ServiceAddon.objects.filter(is_active=True)
    serializer_class = ServiceAddonSerializer
    
    @method_decorator(cache_page(60 * 30))  # Cache for 30 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ServiceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user service history"""
    
    serializer_class = ServiceHistorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Only show current user's service history"""
        if self.request.user.is_authenticated:
            return ServiceHistory.objects.filter(
                user=self.request.user
            ).select_related('service', 'service__category').prefetch_related('addons').order_by('-service_date')
        return ServiceHistory.objects.none()
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent service history (last 5 services)"""
        recent_services = self.get_queryset()[:5]
        serializer = self.get_serializer(recent_services, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user's service statistics"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        history = self.get_queryset()
        
        stats = {
            'total_services': history.count(),
            'total_spent': sum(h.total_amount for h in history),
            'favorite_service': None,
            'last_service': None,
            'services_this_month': history.filter(
                service_date__month=timezone.now().month,
                service_date__year=timezone.now().year
            ).count()
        }
        
        # Get favorite service (most frequently used)
        if history.exists():
            from django.db.models import Count
            favorite = history.values('service__name').annotate(
                count=Count('service')
            ).order_by('-count').first()
            
            if favorite:
                stats['favorite_service'] = favorite['service__name']
            
            # Get last service
            last_service = history.first()
            if last_service:
                stats['last_service'] = {
                    'name': last_service.service.name,
                    'date': last_service.service_date,
                    'rating': last_service.rating
                }
        
        return Response(stats)
