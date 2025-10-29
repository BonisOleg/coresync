"""
DRF Views for Users app.
Safe ViewSets without conflicts with existing code.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login
from django.db.models import Sum, Count
from django.utils import timezone

from .models import User, UserPreference
from .serializers import (
    UserProfileSerializer,
    UserUpdateSerializer,
    UserRegistrationSerializer,
    UserPreferenceSerializer,
    PasswordChangeSerializer,
    BiometricRegistrationSerializer,
    UserStatsSerializer
)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profile management"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only allow users to access their own profile"""
        return User.objects.filter(id=self.request.user.id).select_related('membership', 'membership__plan').prefetch_related('preferences')
    
    def get_object(self):
        """Return current user's profile"""
        return self.request.user
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'create':
            return UserRegistrationSerializer
        return UserProfileSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch', 'put'])
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Return updated profile
            updated_user = UserProfileSerializer(request.user, context={'request': request})
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'user': updated_user.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Password changed successfully'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def register_biometric(self, request):
        """Register biometric authentication data"""
        serializer = BiometricRegistrationSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Biometric authentication registered successfully'
                })
            except Exception as e:
                return Response({
                    'error': f'Biometric registration failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def disable_biometric(self, request):
        """Disable biometric authentication"""
        from .face_recognition_service import delete_user_face_data
        
        result = delete_user_face_data(request.user)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def verify_face(self, request):
        """Verify face against stored biometric data"""
        from .face_recognition_service import verify_user_face
        
        face_data = request.data.get('face_data')
        
        if not face_data:
            return Response({
                'error': 'face_data is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = verify_user_face(request.user, face_data)
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def biometric_status(self, request):
        """Get biometric authentication status"""
        user = request.user
        
        return Response({
            'biometric_enabled': user.biometric_enabled,
            'has_face_data': bool(user.face_recognition_data),
            'last_updated': user.updated_at.isoformat() if user.updated_at else None
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        user = request.user
        
        # Get service history data
        from services.models import ServiceHistory
        service_history = ServiceHistory.objects.filter(user=user)
        
        # Calculate statistics
        total_services = service_history.count()
        total_spent = service_history.aggregate(
            total=Sum('price_paid')
        )['total'] or 0
        
        # Get favorite service
        favorite_service = None
        if service_history.exists():
            favorite = service_history.values('service__name').annotate(
                count=Count('service')
            ).order_by('-count').first()
            if favorite:
                favorite_service = favorite['service__name']
        
        # Get last visit
        last_visit = None
        last_service = service_history.first()
        if last_service:
            last_visit = last_service.service_date
        
        # Services this month
        services_this_month = service_history.filter(
            service_date__month=timezone.now().month,
            service_date__year=timezone.now().year
        ).count()
        
        # Membership info
        membership_level = user.get_membership_status_display()
        member_since = getattr(user.membership, 'start_date', None) if hasattr(user, 'membership') else None
        
        stats_data = {
            'total_services': total_services,
            'total_spent': total_spent,
            'favorite_service': favorite_service,
            'last_visit': last_visit,
            'services_this_month': services_this_month,
            'membership_level': membership_level,
            'member_since': member_since,
            'loyalty_points': 0,  # Future feature
        }
        
        serializer = UserStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get user dashboard data"""
        user = request.user
        
        # Get user profile
        profile_data = UserProfileSerializer(user, context={'request': request}).data
        
        # Get membership info
        membership_data = None
        if hasattr(user, 'membership') and user.membership:
            from memberships.serializers import MembershipSerializer
            membership_data = MembershipSerializer(user.membership).data
        
        # Get recent services
        from services.models import ServiceHistory
        recent_services = ServiceHistory.objects.filter(user=user).order_by('-service_date')[:3]
        from services.serializers import ServiceHistorySerializer
        recent_services_data = ServiceHistorySerializer(recent_services, many=True).data
        
        # Get recommendations (placeholder - would be AI-powered)
        recommendations = [
            {
                'service_name': 'LED Light Therapy',
                'reason': 'Based on your recent facial treatment',
                'suggested_date': timezone.now().date() + timezone.timedelta(days=7)
            },
            {
                'service_name': 'Deep Relaxation Massage',
                'reason': 'You haven\'t had a massage in 3 weeks',
                'suggested_date': timezone.now().date() + timezone.timedelta(days=3)
            }
        ]
        
        dashboard_data = {
            'user': profile_data,
            'membership': membership_data,
            'recent_services': recent_services_data,
            'ai_recommendations': recommendations,
            'quick_stats': {
                'services_this_month': recent_services.filter(
                    service_date__month=timezone.now().month
                ).count(),
                'next_appointment': None,  # Would come from booking system
                'loyalty_level': 'VIP' if user.is_member else 'Guest'
            }
        }
        
        return Response(dashboard_data)


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for user spa preferences"""
    
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show current user's preferences"""
        return UserPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create user preferences"""
        preferences, created = UserPreference.objects.get_or_create(user=self.request.user)
        return preferences
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's preferences"""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch', 'put'])
    def update_preferences(self, request):
        """Update user preferences"""
        preferences = self.get_object()
        serializer = self.get_serializer(
            preferences, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Preferences updated successfully',
                'preferences': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def save_scene(self, request):
        """Save a custom scene configuration"""
        preferences = self.get_object()
        
        scene_name = request.data.get('scene_name')
        scene_config = request.data.get('scene_config', {})
        
        if not scene_name:
            return Response({
                'error': 'scene_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update preferences with new scene
        preferences.default_scene_name = scene_name
        preferences.scene_config = scene_config
        preferences.save()
        
        return Response({
            'success': True,
            'message': f'Scene "{scene_name}" saved successfully',
            'scene_data': {
                'name': scene_name,
                'config': scene_config
            }
        })
    
    @action(detail=False, methods=['post'])
    def reset_preferences(self, request):
        """Reset preferences to defaults"""
        preferences = self.get_object()
        
        # Reset to default values
        preferences.default_scene_name = ''
        preferences.scene_config = {}
        preferences.favorite_scents = []
        preferences.scent_intensity = 3
        preferences.lighting_type = 'warm'
        preferences.lighting_intensity = 70
        preferences.preferred_temperature = 72.0
        preferences.music_genre = ''
        preferences.music_volume = 30
        preferences.save()
        
        serializer = self.get_serializer(preferences)
        return Response({
            'success': True,
            'message': 'Preferences reset to defaults',
            'preferences': serializer.data
        })


class UserRegistrationViewSet(viewsets.ViewSet):
    """ViewSet for user registration (public endpoint)"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate token for immediate login (optional)
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




