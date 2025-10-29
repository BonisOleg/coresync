"""
Booking Management Commands - Manual technician assignment and conflict resolution.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from services.models import Booking
from technicians.models import Technician
from services.booking_validator import BookingValidator
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Assign technician до existing booking з conflict checking'
    
    def add_arguments(self, parser):
        parser.add_argument('booking_id', type=int, help='Booking ID')
        parser.add_argument('technician_id', type=int, help='Technician ID')
        parser.add_argument('--force', action='store_true', help='Force assignment (skip validation)')
    
    def handle(self, *args, **options):
        booking_id = options['booking_id']
        technician_id = options['technician_id']
        force = options.get('force', False)
        
        try:
            booking = Booking.objects.get(id=booking_id)
            technician = Technician.objects.get(id=technician_id)
            
            # Validate спеціалізація
            service_type = self._get_service_type(booking.service.name)
            if service_type not in technician.specialties and 'all' not in technician.specialties:
                self.stdout.write(
                    self.style.ERROR(
                        f'Technician {technician.full_name} не має спеціалізації {service_type}'
                    )
                )
                return
            
            # Validate conflicts
            if not force:
                validation = BookingValidator.validate_no_conflicts(
                    technician_id=technician.id,
                    booking_date=booking.booking_date,
                    start_time=booking.start_time,
                    end_time=booking.end_time,
                    exclude_booking_id=booking_id
                )
                
                if not validation['valid']:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Конфлікт: {validation["error_message"]}'
                        )
                    )
                    self.stdout.write('Конфліктні bookings:')
                    for conflict in validation['conflicts']:
                        self.stdout.write(
                            f'  - {conflict.booking_reference}: '
                            f'{conflict.start_time} - {conflict.end_time}'
                        )
                    return
            
            # Assign technician
            with transaction.atomic():
                old_technician = booking.technician
                booking.technician = technician
                booking.save(update_fields=['technician'])
                
                # Create Google Calendar event
                # from services.google_calendar import calendar_manager
                # event_id = calendar_manager.create_event(booking)
                # if event_id:
                #     booking.google_calendar_event_id = event_id
                #     booking.save(update_fields=['google_calendar_event_id'])
                
                # Send notification
                # from notifications.technician_tasks import send_technician_booking_notification
                # send_technician_booking_notification.delay(booking.id)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Booking {booking.booking_reference} assigned to {technician.full_name}'
                    )
                )
                
                if old_technician:
                    self.stdout.write(f'  Previous: {old_technician.full_name}')
        
        except Booking.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Booking {booking_id} not found'))
        
        except Technician.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Technician {technician_id} not found'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def _get_service_type(self, service_name: str) -> str:
        """Визначає тип сервісу."""
        service_name_lower = service_name.lower()
        
        if 'massage' in service_name_lower:
            return 'massage'
        elif 'facial' in service_name_lower:
            return 'facial'
        elif 'barber' in service_name_lower or 'cut' in service_name_lower:
            return 'barber'
        elif 'mani' in service_name_lower or 'pedi' in service_name_lower:
            return 'manicure'
        else:
            return 'all'

