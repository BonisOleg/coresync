"""
Booking Validation - Перевірка конфліктів перед створенням booking.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from django.db import models
import logging

logger = logging.getLogger(__name__)


class BookingValidator:
    """
    Validates booking requests - запобігає конфліктам та подвійним бронюванням.
    """
    
    @staticmethod
    def validate_no_conflicts(
        technician_id: Optional[int],
        booking_date: datetime.date,
        start_time: datetime.time,
        end_time: datetime.time,
        exclude_booking_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Перевірка конфліктів для technician на specified time.
        
        Args:
            technician_id: ID technician (None якщо не призначено)
            booking_date: Дата booking
            start_time: Час початку
            end_time: Час закінчення
            exclude_booking_id: ID booking для виключення (для update)
        
        Returns:
            Dict: {
                'valid': bool,
                'conflicts': List[Booking],
                'error_message': str
            }
        """
        from services.models import Booking
        
        if not technician_id:
            # Якщо technician не призначено, skip validation
            return {'valid': True, 'conflicts': [], 'error_message': ''}
        
        try:
            # Знаходимо конфлікти
            conflicts_query = Booking.objects.filter(
                technician_id=technician_id,
                booking_date=booking_date,
                status__in=['confirmed', 'pending', 'in_progress']
            ).filter(
                # Overlap logic: new_start < existing_end AND new_end > existing_start
                models.Q(start_time__lt=end_time) &
                models.Q(end_time__gt=start_time)
            )
            
            # Exclude current booking якщо update
            if exclude_booking_id:
                conflicts_query = conflicts_query.exclude(id=exclude_booking_id)
            
            conflicts = list(conflicts_query.select_related('service', 'user'))
            
            if conflicts:
                error_msg = f"Technician busy: {len(conflicts)} conflicting booking(s)"
                logger.warning(error_msg)
                
                return {
                    'valid': False,
                    'conflicts': conflicts,
                    'error_message': error_msg
                }
            
            return {
                'valid': True,
                'conflicts': [],
                'error_message': ''
            }
        
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                'valid': False,
                'conflicts': [],
                'error_message': str(e)
            }
    
    @staticmethod
    def validate_technician_schedule(
        technician_id: int,
        booking_datetime: datetime
    ) -> Dict[str, Any]:
        """
        Перевірка чи technician працює в цей час (згідно Schedule).
        
        Args:
            technician_id: Technician ID
            booking_datetime: Дата та час booking
        
        Returns:
            Dict: {'valid': bool, 'error_message': str}
        """
        from technicians.models import Schedule
        
        try:
            weekday = booking_datetime.weekday()
            booking_time = booking_datetime.time()
            
            # Перевіряємо recurring schedule
            schedules = Schedule.objects.filter(
                technician_id=technician_id,
                is_active=True
            ).filter(
                models.Q(is_recurring=True, weekday=weekday) |
                models.Q(is_recurring=False, specific_date=booking_datetime.date())
            )
            
            # Перевіряємо чи час в межах якогось schedule
            for schedule in schedules:
                if schedule.start_time <= booking_time < schedule.end_time:
                    return {'valid': True, 'error_message': ''}
            
            # Не знайдено відповідного schedule
            return {
                'valid': False,
                'error_message': 'Technician not scheduled for this time'
            }
        
        except Exception as e:
            logger.error(f"Schedule validation error: {str(e)}")
            # Fail open - allow booking
            return {'valid': True, 'error_message': ''}
    
    @staticmethod
    def get_alternative_technicians(
        service_type: str,
        booking_datetime: datetime,
        duration_minutes: int
    ) -> list:
        """
        Знаходить alternative technicians якщо preferred зайнятий.
        
        Returns:
            List[Technician]: Вільні technicians
        """
        from technicians.models import Technician
        
        try:
            # Всі technicians з потрібною спеціалізацією
            technicians = Technician.objects.filter(
                is_active=True
            ).filter(
                models.Q(specialties__contains=[service_type]) |
                models.Q(specialties__contains=['all'])
            )
            
            available = []
            end_datetime = booking_datetime + timedelta(minutes=duration_minutes)
            
            for tech in technicians:
                # Перевірка конфліктів
                validation = BookingValidator.validate_no_conflicts(
                    technician_id=tech.id,
                    booking_date=booking_datetime.date(),
                    start_time=booking_datetime.time(),
                    end_time=end_datetime.time()
                )
                
                if validation['valid']:
                    available.append(tech)
            
            return available
        
        except Exception as e:
            logger.error(f"Get alternatives error: {str(e)}")
            return []

