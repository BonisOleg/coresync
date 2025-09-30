"""
Booking API views for the CoreSync application.
Handles calendar booking with member priority access.
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta, time as dt_time
from django.core.exceptions import ValidationError

from .booking_models import Booking, Room, AvailabilitySlot, BookingAddon
from .models import Service, ServiceAddon
from .serializers import ServiceSerializer
from memberships.models import Membership
from payments.models import Payment, QuickBooksSync

logger = logging.getLogger(__name__)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings with member priority access.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter bookings by user."""
        return Booking.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def availability(self, request):
        """
        Get available booking slots with member priority logic.
        
        Query parameters:
        - date: YYYY-MM-DD (optional, defaults to today)
        - service_id: Service ID (optional)
        - duration: Duration in minutes (optional)
        - room_type: mensuite/private/shared/vip (optional)
        """
        try:
            # Parse parameters
            date_param = request.query_params.get('date')
            service_id = request.query_params.get('service_id')
            duration = request.query_params.get('duration')
            room_type = request.query_params.get('room_type')
            
            # Default to today if no date provided
            if date_param:
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            else:
                target_date = timezone.now().date()
            
            # Check user's booking privileges
            user = request.user
            is_member = hasattr(user, 'membership') and user.membership.is_active
            is_vip = is_member and user.membership.plan.name.lower() == 'unlimited'
            has_priority = is_member and user.membership.plan.priority_booking
            
            # Determine how far ahead user can book
            max_advance_days = self._get_max_advance_days(user)
            max_date = timezone.now().date() + timedelta(days=max_advance_days)
            
            if target_date > max_date:
                return Response({
                    'error': f'Non-members can only book {max_advance_days} days in advance',
                    'max_advance_days': max_advance_days,
                    'is_member': is_member
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Build room filter
            rooms = Room.objects.filter(is_active=True, maintenance_mode=False)
            if room_type:
                rooms = rooms.filter(room_type=room_type)
            
            # Get availability slots for the date
            slots = AvailabilitySlot.objects.filter(
                date=target_date,
                room__in=rooms,
                is_blocked=False
            ).select_related('room')
            
            # Filter by service compatibility if provided
            if service_id:
                try:
                    service = Service.objects.get(id=service_id)
                    # Filter rooms that support this service
                    compatible_rooms = self._get_compatible_rooms(service)
                    slots = slots.filter(room__in=compatible_rooms)
                except Service.DoesNotExist:
                    return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Build response data
            available_slots = []
            now = timezone.now()
            
            for slot in slots:
                if slot.is_available_for_user(user, now):
                    slot_data = {
                        'id': slot.id,
                        'start_time': slot.start_time.strftime('%H:%M'),
                        'end_time': slot.end_time.strftime('%H:%M'),
                        'room_id': slot.room.id,
                        'room_name': slot.room.name,
                        'room_type': slot.room.room_type,
                        'is_premium_slot': slot.is_premium_slot,
                        'available_spots': slot.max_bookings - slot.current_bookings,
                        'max_capacity': slot.max_bookings,
                        'features': slot.room.features,
                        'has_iot_control': slot.room.has_iot_control,
                    }
                    
                    # Add pricing if service specified
                    if service_id:
                        slot_data['price'] = slot.get_price_for_service(service, user)
                        slot_data['member_price'] = service.member_price
                        slot_data['non_member_price'] = service.non_member_price
                    
                    # Add priority info
                    slot_data['priority_info'] = {
                        'is_priority_slot': now < slot.member_only_until,
                        'vip_only': slot.vip_only_until and now < slot.vip_only_until,
                        'member_only_until': slot.member_only_until.isoformat() if slot.member_only_until else None,
                    }
                    
                    available_slots.append(slot_data)
            
            return Response({
                'date': target_date.isoformat(),
                'user_privileges': {
                    'is_member': is_member,
                    'is_vip': is_vip,
                    'has_priority_booking': has_priority,
                    'max_advance_days': max_advance_days,
                    'can_book_priority_slots': has_priority or is_vip,
                },
                'available_slots': available_slots,
                'total_slots': len(available_slots),
            })
            
        except Exception as e:
            return Response({
                'error': f'Error fetching availability: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def create_booking(self, request):
        """
        Create a new booking with member priority validation.
        """
        try:
            data = request.data
            user = request.user
            
            # Validate required fields
            required_fields = ['service_id', 'date', 'start_time', 'room_id']
            for field in required_fields:
                if field not in data:
                    return Response({
                        'error': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get service and room
            try:
                service = Service.objects.get(id=data['service_id'])
                room = Room.objects.get(id=data['room_id'])
            except (Service.DoesNotExist, Room.DoesNotExist) as e:
                return Response({
                    'error': f'Invalid service or room: {str(e)}'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Parse date and time
            booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            
            # Check booking privileges
            max_advance_days = self._get_max_advance_days(user)
            if booking_date > timezone.now().date() + timedelta(days=max_advance_days):
                return Response({
                    'error': f'You can only book {max_advance_days} days in advance',
                    'is_member': hasattr(user, 'membership') and user.membership.is_active
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Find availability slot
            try:
                slot = AvailabilitySlot.objects.get(
                    date=booking_date,
                    start_time=start_time,
                    room=room
                )
            except AvailabilitySlot.DoesNotExist:
                return Response({
                    'error': 'No availability slot found for this time'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if slot is available for user
            if not slot.is_available_for_user(user):
                return Response({
                    'error': 'This time slot is not available for your membership level',
                    'priority_info': {
                        'member_only_until': slot.member_only_until.isoformat(),
                        'vip_only_until': slot.vip_only_until.isoformat() if slot.vip_only_until else None,
                    }
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Create booking
            booking_data = {
                'service': service,
                'room': room,
                'booking_date': booking_date,
                'start_time': start_time,
                'duration': service.duration,
                'base_price': slot.get_price_for_service(service, user),
            }
            
            # Add optional fields
            optional_fields = ['guest_name', 'guest_phone', 'guest_email', 
                             'special_requests', 'ai_program']
            for field in optional_fields:
                if field in data:
                    booking_data[field] = data[field]
            
            # Handle IoT scene preferences
            if 'scene_preferences' in data:
                booking_data['scene_preferences'] = data['scene_preferences']
            
            # Create the booking
            booking = Booking.objects.create(user=user, **booking_data)
            
            # Handle add-ons
            if 'addons' in data:
                self._process_booking_addons(booking, data['addons'])
            
            # Calculate final total
            booking.calculate_total()
            booking.save()
            
            # Update slot availability
            slot.current_bookings += 1
            slot.save()
            
            # Create payment record for QuickBooks integration
            payment = self._create_booking_payment(booking, data.get('payment_method', 'pending'))
            
            # Schedule QuickBooks sync
            self._schedule_quickbooks_sync(booking, 'invoice')
            
            return Response({
                'id': booking.id,
                'booking_reference': booking.booking_reference,
                'service': ServiceSerializer(service).data,
                'date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'room': {
                    'id': room.id,
                    'name': room.name,
                    'type': room.room_type,
                },
                'pricing': {
                    'base_price': str(booking.base_price),
                    'addons_total': str(booking.addons_total),
                    'discount_applied': str(booking.discount_applied),
                    'final_total': str(booking.final_total),
                },
                'status': booking.status,
                'payment_status': booking.payment_status,
                'confirmation_sent': True,  # Will implement email confirmation
            })
            
        except Exception as e:
            return Response({
                'error': f'Error creating booking: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get user's bookings (upcoming and past)."""
        user = request.user
        now = timezone.now()
        today = now.date()
        
        # Upcoming bookings
        upcoming = Booking.objects.filter(
            user=user,
            booking_date__gte=today,
            status__in=['confirmed', 'pending']
        ).select_related('service', 'room').order_by('booking_date', 'start_time')
        
        # Past bookings (last 6 months)
        six_months_ago = today - timedelta(days=180)
        past = Booking.objects.filter(
            user=user,
            booking_date__gte=six_months_ago,
            booking_date__lt=today,
            status__in=['completed', 'cancelled', 'no_show']
        ).select_related('service', 'room').order_by('-booking_date', '-start_time')
        
        def serialize_booking(booking):
            return {
                'id': booking.id,
                'booking_reference': booking.booking_reference,
                'service': booking.service.name,
                'service_category': booking.service.category.name,
                'date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'room': booking.room.name,
                'status': booking.status,
                'can_cancel': booking.can_cancel(),
                'can_reschedule': booking.can_reschedule(),
                'final_total': str(booking.final_total),
                'payment_status': booking.payment_status,
            }
        
        return Response({
            'upcoming': [serialize_booking(b) for b in upcoming[:10]],
            'past': [serialize_booking(b) for b in past[:20]],
            'total_upcoming': upcoming.count(),
            'total_past': past.count(),
        })
    
    @action(detail=True, methods=['post'])
    def cancel_booking(self, request, pk=None):
        """Cancel a booking with proper validation."""
        try:
            booking = self.get_object()
            
            if not booking.can_cancel():
                return Response({
                    'error': 'This booking cannot be cancelled (too late or already completed)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get cancellation reason
            reason = request.data.get('reason', 'Cancelled by customer')
            
            # Cancel the booking
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.cancellation_reason = reason
            booking.save()
            
            # Free up the slot
            try:
                slot = AvailabilitySlot.objects.get(
                    date=booking.booking_date,
                    start_time=booking.start_time,
                    room=booking.room
                )
                slot.current_bookings = max(0, slot.current_bookings - 1)
                slot.save()
            except AvailabilitySlot.DoesNotExist:
                pass
            
            # Schedule QuickBooks sync for cancellation
            self._schedule_quickbooks_sync(booking, 'invoice')
            
            return Response({
                'message': 'Booking cancelled successfully',
                'booking_reference': booking.booking_reference,
                'status': booking.status,
            })
            
        except Exception as e:
            return Response({
                'error': f'Error cancelling booking: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_max_advance_days(self, user):
        """Get maximum days a user can book in advance."""
        if hasattr(user, 'membership') and user.membership.is_active:
            membership = user.membership
            if membership.plan.name.lower() == 'unlimited':
                return 90  # 3 months for VIP
            elif membership.plan.priority_booking:
                return 60   # 2 months for priority members
            else:
                return 30   # 1 month for regular members
        return 3  # 3 days for non-members
    
    def _get_compatible_rooms(self, service):
        """Get rooms compatible with a service."""
        # Logic to determine which rooms support which services
        service_category = service.category.slug
        
        if service_category == 'mensuite':
            return Room.objects.filter(room_type__in=['mensuite', 'shared'])
        elif service_category == 'coresync-private':
            return Room.objects.filter(room_type__in=['private', 'vip'])
        else:
            return Room.objects.filter(is_active=True)
    
    def _process_booking_addons(self, booking, addons_data):
        """Process and create booking add-ons."""
        for addon_data in addons_data:
            try:
                addon = ServiceAddon.objects.get(id=addon_data['id'])
                quantity = addon_data.get('quantity', 1)
                
                BookingAddon.objects.create(
                    booking=booking,
                    addon=addon,
                    quantity=quantity,
                    unit_price=addon.price,
                    notes=addon_data.get('notes', ''),
                    preferences=addon_data.get('preferences', {})
                )
            except ServiceAddon.DoesNotExist:
                continue
    
    def _create_booking_payment(self, booking, payment_method='pending'):
        """Create payment record for booking - ensures ALL payments go to QuickBooks."""
        from payments.models import Payment
        
        try:
            payment = Payment.objects.create(
                user=booking.user,
                payment_type='service',
                payment_method=payment_method if payment_method != 'pending' else 'stripe_card',
                amount=booking.final_total,
                currency='USD',
                status='pending',  # Will be updated by Stripe webhook
                description=f"Service booking: {booking.service.name}",
                metadata={
                    'booking_id': booking.id,
                    'booking_reference': booking.booking_reference,
                    'service_name': booking.service.name,
                    'room_name': booking.room.name,
                    'booking_date': booking.booking_date.isoformat(),
                }
            )
            
            # Link payment to booking
            booking.payment_status = 'pending'
            booking.stripe_payment_intent_id = f"pending_{payment.payment_id}"
            booking.save()
            
            logger.info(f"Created payment record {payment.payment_id} for booking {booking.booking_reference}")
            return payment
            
        except Exception as e:
            logger.error(f"Failed to create payment for booking {booking.booking_reference}: {e}")
            return None

    def _schedule_quickbooks_sync(self, booking, sync_type='invoice'):
        """Schedule QuickBooks synchronization for booking."""
        try:
            QuickBooksSync.objects.get_or_create(
                sync_type=sync_type,
                object_id=str(booking.id),
                defaults={
                    'status': 'pending',
                    'sync_data': {
                        'booking_reference': booking.booking_reference,
                        'customer_name': booking.user.full_name,
                        'service_name': booking.service.name,
                        'total_amount': str(booking.final_total),
                        'booking_date': booking.booking_date.isoformat(),
                    }
                }
            )
        except Exception as e:
            # Log error but don't fail the booking
            print(f"QuickBooks sync scheduling failed: {e}")


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for room information.
    """
    queryset = Room.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        """List all available rooms."""
        rooms = self.get_queryset()
        
        room_data = []
        for room in rooms:
            room_data.append({
                'id': room.id,
                'name': room.name,
                'type': room.room_type,
                'capacity': room.capacity,
                'features': room.features,
                'has_iot_control': room.has_iot_control,
                'premium_modifier': str(room.premium_modifier),
                'operating_hours': {
                    'opening': room.opening_time.strftime('%H:%M'),
                    'closing': room.closing_time.strftime('%H:%M'),
                }
            })
        
        return Response({
            'rooms': room_data,
            'total_rooms': len(room_data)
        })
    
    @action(detail=True, methods=['get'])
    def availability_calendar(self, request, pk=None):
        """Get availability calendar for a specific room."""
        room = self.get_object()
        
        # Get date range (default: next 30 days)
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        # Get availability slots
        slots = AvailabilitySlot.objects.filter(
            room=room,
            date__range=[start_date, end_date]
        ).order_by('date', 'start_time')
        
        # Group by date
        calendar_data = {}
        for slot in slots:
            date_str = slot.date.isoformat()
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            
            calendar_data[date_str].append({
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'available_spots': slot.max_bookings - slot.current_bookings,
                'is_premium': slot.is_premium_slot,
                'member_only_until': slot.member_only_until.isoformat(),
            })
        
        return Response({
            'room': room.name,
            'calendar': calendar_data,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            }
        })
