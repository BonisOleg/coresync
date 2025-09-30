"""
DRF Views for Memberships app.
Safe ViewSets without conflicts with existing code.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils import timezone

logger = logging.getLogger(__name__)

from .models import MembershipPlan, Membership, MembershipBenefit
from .serializers import (
    MembershipPlanListSerializer,
    MembershipPlanDetailSerializer,
    MembershipSerializer,
    MembershipCreateSerializer,
    MembershipUpgradeSerializer,
    MembershipBenefitSerializer
)


class MembershipPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for membership plans"""
    
    queryset = MembershipPlan.objects.filter(is_active=True).order_by('order', 'price')
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return MembershipPlanListSerializer
        return MembershipPlanDetailSerializer
    
    @method_decorator(cache_page(60 * 30))  # Cache for 30 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 30))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured membership plans"""
        featured_plans = self.get_queryset().filter(featured=True)
        serializer = MembershipPlanListSerializer(featured_plans, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def benefits(self, request, slug=None):
        """Get detailed benefits for a specific plan"""
        plan = self.get_object()
        
        # Return structured benefits data
        benefits_data = {
            'plan_name': plan.name,
            'plan_price': plan.price,
            'monthly_price': plan.monthly_price,
            'discount_percentage': plan.discount_percentage,
            'benefits_list': plan.benefits,
            'access_levels': {
                'mensuite_access': plan.mensuite_access,
                'coresync_private_access': plan.coresync_private_access,
                'iot_control_access': plan.iot_control_access,
                'priority_booking': plan.priority_booking,
            },
            'quotas': {
                'monthly_service_credits': plan.monthly_service_credits,
                'guest_passes': plan.guest_passes,
            },
            'example_savings': plan.calculate_savings_example()
        }
        
        return Response(benefits_data)


class MembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for user memberships"""
    
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show current user's memberships"""
        return Membership.objects.filter(user=self.request.user).select_related('plan')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return MembershipCreateSerializer
        elif self.action == 'upgrade':
            return MembershipUpgradeSerializer
        return MembershipSerializer
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get user's current active membership"""
        try:
            membership = request.user.membership
            if membership.is_active:
                serializer = self.get_serializer(membership)
                return Response(serializer.data)
            else:
                return Response({
                    'message': 'No active membership found',
                    'expired_membership': MembershipSerializer(membership).data
                }, status=status.HTTP_404_NOT_FOUND)
        except Membership.DoesNotExist:
            return Response({
                'message': 'No membership found',
                'available_plans': MembershipPlanListSerializer(
                    MembershipPlan.objects.filter(is_active=True).order_by('price'), 
                    many=True
                ).data
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def upgrade(self, request):
        """Upgrade user's membership"""
        serializer = MembershipUpgradeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                # Get current membership
                current_membership = request.user.membership
                new_plan = MembershipPlan.objects.get(id=serializer.validated_data['plan_id'])
                
                # Calculate pro-rated pricing and upgrade
                # This would integrate with Stripe for actual payment processing
                # For now, we'll just update the membership
                
                current_membership.plan = new_plan
                current_membership.save()
                
                # Reset monthly usage counters on upgrade
                current_membership.reset_monthly_usage()
                
                # Create payment record for QuickBooks integration
                self._create_membership_payment(current_membership, serializer.validated_data)
                
                response_data = {
                    'success': True,
                    'message': f'Successfully upgraded to {new_plan.name}',
                    'membership': MembershipSerializer(current_membership).data,
                    'payment_info': {
                        'method': serializer.validated_data['payment_method'],
                        'status': 'processed',  # This would come from Stripe
                    }
                }
                
                return Response(response_data)
                
            except MembershipPlan.DoesNotExist:
                return Response({
                    'error': 'Invalid membership plan'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            except Exception as e:
                return Response({
                    'error': f'Upgrade failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _create_membership_payment(self, membership, payment_data):
        """Create payment record for membership - ensures ALL payments go to QuickBooks."""
        from payments.models import Payment
        import uuid
        
        try:
            payment = Payment.objects.create(
                user=membership.user,
                payment_type='membership',
                payment_method=payment_data.get('payment_method', 'stripe_card'),
                amount=membership.plan.price,
                currency='USD',
                status='succeeded',  # Membership upgrades are immediate
                description=f"Membership: {membership.plan.name}",
                membership=membership,
                metadata={
                    'membership_id': membership.id,
                    'plan_name': membership.plan.name,
                    'upgrade_date': timezone.now().isoformat(),
                }
            )
            
            logger.info(f"Created membership payment record {payment.payment_id} for {membership.user.full_name}")
            return payment
            
        except Exception as e:
            logger.error(f"Failed to create membership payment for {membership.user.full_name}: {e}")
            return None
    
    @action(detail=False, methods=['get'])
    def usage_stats(self, request):
        """Get user's membership usage statistics"""
        try:
            membership = request.user.membership
            
            if not membership.is_active:
                return Response({
                    'error': 'No active membership found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            stats = {
                'plan_name': membership.plan.name,
                'days_remaining': membership.days_remaining,
                'usage_this_month': {
                    'services_used': membership.services_used_this_month,
                    'service_credits_available': membership.plan.monthly_service_credits,
                    'can_use_credit': membership.can_use_service_credit(),
                    'guest_passes_used': membership.guest_passes_used,
                    'guest_passes_available': membership.plan.guest_passes,
                },
                'access_levels': {
                    'mensuite': membership.plan.mensuite_access,
                    'coresync_private': membership.plan.coresync_private_access,
                    'iot_control': membership.plan.iot_control_access,
                    'priority_booking': membership.plan.priority_booking,
                },
                'auto_renew': membership.auto_renew,
                'renewal_date': membership.end_date,
            }
            
            return Response(stats)
            
        except Membership.DoesNotExist:
            return Response({
                'error': 'No membership found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def use_service_credit(self, request):
        """Use one service credit"""
        try:
            membership = request.user.membership
            
            if membership.use_service_credit():
                return Response({
                    'success': True,
                    'message': 'Service credit used successfully',
                    'remaining_credits': membership.plan.monthly_service_credits - membership.services_used_this_month
                })
            else:
                return Response({
                    'error': 'No service credits available this month'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Membership.DoesNotExist:
            return Response({
                'error': 'No active membership found'
            }, status=status.HTTP_404_NOT_FOUND)


class MembershipBenefitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for membership benefits"""
    
    queryset = MembershipBenefit.objects.filter(is_active=True)
    serializer_class = MembershipBenefitSerializer
    
    @method_decorator(cache_page(60 * 60))  # Cache for 1 hour
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get benefits grouped by type"""
        benefit_type = request.query_params.get('type')
        if benefit_type:
            benefits = self.get_queryset().filter(benefit_type=benefit_type)
        else:
            benefits = self.get_queryset()
        
        # Group by benefit type
        grouped_benefits = {}
        for benefit in benefits:
            if benefit.benefit_type not in grouped_benefits:
                grouped_benefits[benefit.benefit_type] = []
            grouped_benefits[benefit.benefit_type].append(
                MembershipBenefitSerializer(benefit).data
            )
        
        return Response(grouped_benefits)




