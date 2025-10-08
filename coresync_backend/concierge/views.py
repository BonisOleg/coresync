"""Views for Concierge app."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import ConciergeRequest
from .serializers import (
    ConciergeRequestListSerializer,
    ConciergeRequestDetailSerializer,
    CreateConciergeRequestSerializer
)


class ConciergeRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for concierge requests."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateConciergeRequestSerializer
        elif self.action == 'retrieve':
            return ConciergeRequestDetailSerializer
        return ConciergeRequestListSerializer
    
    def get_queryset(self):
        """Get user's concierge requests."""
        return ConciergeRequest.objects.filter(
            user=self.request.user
        ).select_related(
            'user',
            'payment',
            'pickup_booking'
        ).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create new concierge request."""
        serializer = CreateConciergeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            # Check if alcohol request
            requires_age_verification = data['request_type'] == 'alcohol'
            
            # Create request
            concierge_request = ConciergeRequest.objects.create(
                user=request.user,
                request_type=data['request_type'],
                title=data['title'],
                description=data['description'],
                product_link=data.get('product_link', ''),
                budget_min=data['budget_min'],
                budget_max=data['budget_max'],
                preferred_pickup_date=data['preferred_pickup_date'],
                requires_age_verification=requires_age_verification,
                attachments=data.get('attachments', [])
            )
            
            # Return created request
            response_serializer = ConciergeRequestDetailSerializer(concierge_request)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'Error creating request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel_request(self, request, pk=None):
        """Cancel concierge request."""
        concierge_request = self.get_object()
        
        if not concierge_request.can_be_cancelled:
            return Response(
                {'error': 'Request cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel request
        concierge_request.status = 'cancelled'
        concierge_request.save()
        
        return Response({
            'message': 'Request cancelled successfully',
            'request_number': concierge_request.request_number
        })
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get user's requests grouped by status."""
        queryset = self.get_queryset()
        
        pending = queryset.filter(status='pending')
        active = queryset.filter(status__in=['approved', 'processing'])
        completed = queryset.filter(status__in=['ready', 'completed'])
        
        return Response({
            'pending': ConciergeRequestListSerializer(pending, many=True).data,
            'active': ConciergeRequestListSerializer(active, many=True).data,
            'completed': ConciergeRequestListSerializer(completed, many=True).data,
        })
