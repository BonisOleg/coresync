"""
Booking Orchestrator - AI Agent → Booking System Integration.
Handles availability checks, booking creation, payment flow.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class BookingOrchestrator:
    """
    Orchestrates booking process від AI conversation до confirmed booking.
    Integrates: services.Booking, payments, calendar, notifications.
    """
    
    def __init__(self):
        # Lazy imports для уникнення circular dependencies
        pass
    
    async def check_availability(
        self,
        service_id: int,
        preferred_date: datetime,
        duration_minutes: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Check availability для service на specified date.
        
        Args:
            service_id: Service ID
            preferred_date: Preferred date/time
            duration_minutes: Service duration
            user_id: User ID (для membership tier check)
        
        Returns:
            Dict: {
                'available': bool,
                'suggested_slots': List[datetime],
                'restrictions': Dict (membership-based)
            }
        """
        try:
            from services.models import Service, Booking
            from users.models import User
            
            # Get service
            service = await self._get_service(service_id)
            
            # Check membership restrictions
            restrictions = await self._check_membership_restrictions(
                user_id, preferred_date
            )
            
            if not restrictions['allowed']:
                return {
                    'available': False,
                    'reason': restrictions['reason'],
                    'suggested_slots': [],
                    'restrictions': restrictions
                }
            
            # TODO: Check Google Calendar API (після payment card)
            # For now: check Django Booking model
            
            from asgiref.sync import sync_to_async
            
            # Query existing bookings
            existing_bookings = await sync_to_async(
                lambda: list(Booking.objects.filter(
                    service=service,
                    booking_date=preferred_date.date(),
                    status__in=['confirmed', 'pending']
                ))
            )()
            
            # Simple availability check (буде замінено Google Calendar)
            is_available = len(existing_bookings) < 10  # Placeholder logic
            
            # Generate suggested slots
            suggested_slots = await self._generate_suggested_slots(
                preferred_date, duration_minutes, existing_bookings
            )
            
            return {
                'available': is_available,
                'preferred_slot': preferred_date,
                'suggested_slots': suggested_slots[:5],  # Top 5 alternatives
                'restrictions': restrictions,
                'service_name': service.name
            }
        
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return {
                'available': False,
                'error': str(e),
                'suggested_slots': []
            }
    
    async def create_booking(
        self,
        service_id: int,
        user_id: int,
        booking_datetime: datetime,
        addons: Optional[List[int]] = None,
        special_requests: Optional[str] = None,
        conversation_session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create booking with atomic transaction.
        
        Args:
            service_id: Service ID
            user_id: User ID
            booking_datetime: Booking date/time
            addons: List of addon IDs
            special_requests: Special requests text
            conversation_session_id: AI conversation session ID
        
        Returns:
            Dict: {
                'booking_id': int,
                'status': str,
                'payment_required': bool,
                'total_price': Decimal
            }
        """
        try:
            from services.models import Service, Booking
            from users.models import User
            from asgiref.sync import sync_to_async
            
            # Atomic transaction
            with transaction.atomic():
                # Get service and user
                service = await self._get_service(service_id)
                user = await self._get_user(user_id)
                
                # Знаходимо вільного technician з validation
                available_technician = await self._find_available_technician(
                    service=service,
                    booking_datetime=booking_datetime
                )
                
                if not available_technician:
                    logger.warning(f"No available technician for service {service_id}")
                    # Продовжуємо без technician, можна призначити пізніше manually
                else:
                    # Double-check validation перед створенням
                    from services.booking_validator import BookingValidator
                    
                    end_datetime = booking_datetime + timedelta(minutes=service.duration)
                    validation = await sync_to_async(
                        BookingValidator.validate_no_conflicts
                    )(
                        technician_id=available_technician.id,
                        booking_date=booking_datetime.date(),
                        start_time=booking_datetime.time(),
                        end_time=end_datetime.time()
                    )
                    
                    if not validation['valid']:
                        logger.error(f"Validation failed: {validation['error_message']}")
                        raise ValueError(validation['error_message'])
                
                # Calculate pricing (membership-aware)
                pricing = await self.calculate_pricing(
                    service_id=service_id,
                    user_id=user_id,
                    addons=addons
                )
                
                # Create booking
                booking_data = {
                    'service': service,
                    'user': user,
                    'booking_date': booking_datetime.date(),
                    'booking_time': booking_datetime.time(),
                    'status': 'pending',  # Pending until payment
                    'total_price': pricing['total_price'],
                    'special_requests': special_requests or '',
                    'technician': available_technician,  # Призначаємо technician
                }
                
                booking = await sync_to_async(Booking.objects.create)(**booking_data)
                
                # Link conversation
                if conversation_session_id:
                    await self._link_conversation_to_booking(
                        conversation_session_id, booking.id
                    )
                
                # Create Google Calendar events (після payment card)
                # from services.google_calendar import calendar_manager
                # event_id = calendar_manager.create_event(booking)
                # if event_id:
                #     booking.google_calendar_event_id = event_id
                #     await sync_to_async(booking.save)(update_fields=['google_calendar_event_id'])
                
                logger.info(f"Booking created: {booking.id}, technician: {available_technician}")
                
                return {
                    'booking_id': booking.id,
                    'status': 'pending_payment',
                    'payment_required': True,
                    'total_price': float(pricing['total_price']),
                    'currency': 'USD',
                    'booking_reference': f"CS-{booking.id}",
                    'technician': available_technician.full_name if available_technician else None
                }
        
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            raise
    
    async def calculate_pricing(
        self,
        service_id: int,
        user_id: Optional[int],
        addons: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Calculate pricing з membership discounts.
        
        Args:
            service_id: Service ID
            user_id: User ID (для membership check)
            addons: List of addon IDs
        
        Returns:
            Dict: {
                'base_price': Decimal,
                'discount': Decimal,
                'total_price': Decimal,
                'membership_tier': str
            }
        """
        try:
            from services.models import Service
            from memberships.models import Membership
            from decimal import Decimal
            
            # Get service
            service = await self._get_service(service_id)
            base_price = service.base_price
            
            # Check membership tier
            membership_tier = None
            discount_percent = Decimal('0')
            
            if user_id:
                try:
                    from asgiref.sync import sync_to_async
                    
                    membership = await sync_to_async(
                        lambda: Membership.objects.filter(
                            user_id=user_id,
                            status='active'
                        ).first()
                    )()
                    
                    if membership:
                        membership_tier = membership.tier
                        # Discount mapping (згідно CORESYNC_PROJECT_FINAL.md)
                        discount_mapping = {
                            'base': Decimal('0.30'),  # 30%
                            'premium': Decimal('0.40'),  # 40%
                            'unlimited': Decimal('1.00')  # Free
                        }
                        discount_percent = discount_mapping.get(
                            membership_tier, 
                            Decimal('0')
                        )
                
                except Exception as e:
                    logger.warning(f"Error checking membership: {str(e)}")
            
            # Calculate discount
            discount_amount = base_price * discount_percent
            total_price = base_price - discount_amount
            
            # TODO: Add addons pricing
            
            return {
                'base_price': float(base_price),
                'discount_percent': float(discount_percent * 100),
                'discount_amount': float(discount_amount),
                'total_price': float(total_price),
                'membership_tier': membership_tier or 'non_member',
                'currency': 'USD'
            }
        
        except Exception as e:
            logger.error(f"Error calculating pricing: {str(e)}")
            raise
    
    async def _check_membership_restrictions(
        self,
        user_id: Optional[int],
        booking_date: datetime
    ) -> Dict[str, Any]:
        """
        Check membership-based booking restrictions.
        Members: 2-3 міс вперед
        Non-members: 3 дні
        """
        try:
            from memberships.models import Membership
            from asgiref.sync import sync_to_async
            
            today = timezone.now()
            days_ahead = (booking_date - today).days
            
            # Non-member restriction: 3 дні
            max_days_non_member = 3
            
            if not user_id:
                if days_ahead > max_days_non_member:
                    return {
                        'allowed': False,
                        'reason': f'Non-members can book max {max_days_non_member} days ahead. Consider membership!',
                        'max_days': max_days_non_member
                    }
                return {'allowed': True}
            
            # Check membership tier
            membership = await sync_to_async(
                lambda: Membership.objects.filter(
                    user_id=user_id,
                    status='active'
                ).first()
            )()
            
            if not membership:
                # Registered but no membership
                if days_ahead > max_days_non_member:
                    return {
                        'allowed': False,
                        'reason': 'Upgrade to membership for advance booking!',
                        'max_days': max_days_non_member
                    }
                return {'allowed': True}
            
            # Member restrictions
            max_days_mapping = {
                'base': 60,  # 2 місяці
                'premium': 90,  # 3 місяці
                'unlimited': 90
            }
            
            max_days = max_days_mapping.get(membership.tier, max_days_non_member)
            
            if days_ahead > max_days:
                return {
                    'allowed': False,
                    'reason': f'{membership.tier.title()} members can book up to {max_days} days ahead.',
                    'max_days': max_days
                }
            
            return {
                'allowed': True,
                'membership_tier': membership.tier,
                'max_days': max_days
            }
        
        except Exception as e:
            logger.error(f"Error checking restrictions: {str(e)}")
            return {'allowed': True}  # Fail open
    
    async def _generate_suggested_slots(
        self,
        preferred_date: datetime,
        duration_minutes: int,
        existing_bookings: List
    ) -> List[datetime]:
        """Generate alternative time slots."""
        suggestions = []
        
        # Simple logic: next 5 days, 10AM-8PM slots
        for day_offset in range(5):
            date = preferred_date + timedelta(days=day_offset)
            
            for hour in range(10, 20):  # 10AM to 8PM
                slot = date.replace(hour=hour, minute=0, second=0)
                suggestions.append(slot)
        
        return suggestions[:10]  # Top 10
    
    async def _get_service(self, service_id: int):
        """Get service by ID."""
        from services.models import Service
        from asgiref.sync import sync_to_async
        
        return await sync_to_async(Service.objects.get)(id=service_id)
    
    async def _get_user(self, user_id: int):
        """Get user by ID."""
        from users.models import User
        from asgiref.sync import sync_to_async
        
        return await sync_to_async(User.objects.get)(id=user_id)
    
    async def _find_available_technician(
        self,
        service,
        booking_datetime: datetime
    ):
        """
        Знаходить вільного technician з потрібною спеціалізацією.
        Перевіряє конфлікти з існуючими bookings.
        
        Args:
            service: Service object
            booking_datetime: Дата та час booking
        
        Returns:
            Technician object або None
        """
        try:
            from technicians.models import Technician
            from services.models import Booking
            from django.db import models
            from asgiref.sync import sync_to_async
            
            # Визначаємо тип сервісу для matching specialties
            service_type = self._get_service_type(service.name)
            
            # Знаходимо technicians з потрібною спеціалізацією
            technicians = await sync_to_async(
                lambda: list(Technician.objects.filter(
                    is_active=True
                ).filter(
                    models.Q(specialties__contains=[service_type]) |
                    models.Q(specialties__contains=['all'])
                ))
            )()
            
            if not technicians:
                logger.warning(f"No technicians found for service type: {service_type}")
                return None
            
            # Обчислюємо end_time
            end_datetime = booking_datetime + timedelta(minutes=service.duration)
            
            # Перевіряємо кожного technician на конфлікти
            for tech in technicians:
                has_conflict = await sync_to_async(
                    lambda: Booking.objects.filter(
                        technician=tech,
                        booking_date=booking_datetime.date(),
                        status__in=['confirmed', 'pending', 'in_progress']
                    ).filter(
                        # Перевірка overlap: new_start < existing_end AND new_end > existing_start
                        models.Q(start_time__lt=end_datetime.time()) &
                        models.Q(end_time__gt=booking_datetime.time())
                    ).exists()
                )()
                
                if not has_conflict:
                    logger.info(f"Found available technician: {tech.full_name}")
                    return tech
            
            # Жоден technician не вільний
            logger.warning(f"All technicians busy for {booking_datetime}")
            return None
        
        except Exception as e:
            logger.error(f"Error finding available technician: {str(e)}")
            return None
    
    def _get_service_type(self, service_name: str) -> str:
        """Визначає тип сервісу з назви."""
        service_name_lower = service_name.lower()
        
        if 'massage' in service_name_lower or 'масаж' in service_name_lower:
            return 'massage'
        elif 'facial' in service_name_lower or 'фейшал' in service_name_lower:
            return 'facial'
        elif 'barber' in service_name_lower or 'барбер' in service_name_lower or 'cut' in service_name_lower:
            return 'barber'
        elif 'mani' in service_name_lower or 'pedi' in service_name_lower:
            return 'manicure'
        else:
            return 'all'
    
    async def _link_conversation_to_booking(
        self,
        session_id: str,
        booking_id: int
    ):
        """Link AI conversation to booking."""
        try:
            from ai_agent.models import Conversation
            from services.models import Booking
            from asgiref.sync import sync_to_async
            
            conversation = await sync_to_async(
                Conversation.objects.get
            )(session_id=session_id)
            
            booking = await sync_to_async(
                Booking.objects.get
            )(id=booking_id)
            
            conversation.booking = booking
            await sync_to_async(conversation.save)(update_fields=['booking'])
            
            logger.info(f"Linked conversation {session_id} to booking {booking_id}")
        
        except Exception as e:
            logger.error(f"Error linking conversation: {str(e)}")

