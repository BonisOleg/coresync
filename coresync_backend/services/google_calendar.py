"""
Google Calendar Integration - Booking calendar management.
BLOCKED: потребує payment card для Google Cloud.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CalendarManager:
    """
    Google Calendar API wrapper для CoreSync bookings.
    Singleton pattern - один instance для всього проекту.
    
    TODO: Activate після Google Cloud payment card setup.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        from django.conf import settings
        
        self.service_account_file = getattr(
            settings, 
            'GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE', 
            None
        )
        
        # 3 календарі (згідно Full100.md)
        self.calendars = {
            'master': None,  # Master Booking Calendar (public read)
            'technicians': None,  # Technician Schedules (shared)
            'private': None,  # Private Spa Bookings (restricted)
        }
        
        self.service = None
        self._initialized = True
        
        if not self.service_account_file:
            logger.warning("Google Calendar service account not configured")
    
    def _get_service(self):
        """
        Initialize Google Calendar API service.
        
        TODO: Implement після Google Cloud setup.
        """
        if self.service:
            return self.service
        
        if not self.service_account_file:
            logger.warning("Google Calendar not configured")
            return None
        
        try:
            # TODO: Implement після Google APIs package install
            # from google.oauth2 import service_account
            # from googleapiclient.discovery import build
            
            # credentials = service_account.Credentials.from_service_account_file(
            #     self.service_account_file,
            #     scopes=['https://www.googleapis.com/auth/calendar']
            # )
            
            # self.service = build('calendar', 'v3', credentials=credentials)
            # return self.service
            
            logger.info("Google Calendar service (TODO: implement)")
            return None
        
        except Exception as e:
            logger.error(f"Google Calendar init error: {str(e)}")
            return None
    
    def create_event(self, booking) -> Optional[str]:
        """
        Create calendar events у ВСІХ потрібних календарях.
        Блокує час для technician та додає в master calendar.
        
        Args:
            booking: Booking object
        
        Returns:
            str: Master event ID або None
        """
        service = self._get_service()
        if not service:
            logger.info(f"Would create calendar events for booking {booking.id}")
            return None
        
        try:
            # TODO: Implement після Google Calendar API ready
            # Prepare event data
            start_datetime = datetime.combine(
                booking.booking_date, 
                booking.start_time
            )
            end_datetime = start_datetime + timedelta(minutes=booking.duration)
            
            event_data = {
                'summary': f'{booking.user.get_full_name()} - {booking.service.name}',
                'description': self._format_event_description(booking),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'attendees': self._get_attendees(booking),
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24hrs
                        {'method': 'popup', 'minutes': 60},  # 1hr
                    ],
                },
                'extendedProperties': {
                    'private': {
                        'booking_id': str(booking.id),
                        'booking_reference': booking.booking_reference,
                        'technician_id': str(booking.technician.id) if booking.technician else '',
                    }
                }
            }
            
            master_event_id = None
            
            # 1. MASTER CALENDAR - всі bookings (public read)
            # master_event = service.events().insert(
            #     calendarId=self.calendars['master'],
            #     body=event_data
            # ).execute()
            # master_event_id = master_event.get('id')
            
            # 2. TECHNICIAN CALENDAR - блокує час для конкретного technician
            if booking.technician:
                # technician_event_data = {
                #     **event_data,
                #     'summary': f'BLOCKED - {booking.service.name}',
                #     'colorId': '11',  # Red color для blocked slots
                # }
                # service.events().insert(
                #     calendarId=self.calendars['technicians'],
                #     body=technician_event_data
                # ).execute()
                logger.info(f"Would block technician {booking.technician.full_name} calendar")
            
            # 3. PRIVATE CALENDAR - якщо Coresync Private service
            if 'private' in booking.service.name.lower():
                # service.events().insert(
                #     calendarId=self.calendars['private'],
                #     body=event_data
                # ).execute()
                logger.info(f"Would add to private calendar")
            
            logger.info(f"Would create events in multiple calendars for booking {booking.id}")
            return f"test-event-{booking.id}"
        
        except Exception as e:
            logger.error(f"Calendar create event error: {str(e)}")
            return None
    
    def update_event(self, event_id: str, booking) -> bool:
        """Update existing calendar event."""
        service = self._get_service()
        if not service:
            return False
        
        try:
            # TODO: Implement
            logger.info(f"Would update event {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Calendar update event error: {str(e)}")
            return False
    
    def delete_event(self, event_id: str, calendar_type: str = 'master') -> bool:
        """Delete calendar event."""
        service = self._get_service()
        if not service:
            return False
        
        try:
            # TODO: Implement
            # calendar_id = self.calendars.get(calendar_type)
            # service.events().delete(
            #     calendarId=calendar_id,
            #     eventId=event_id
            # ).execute()
            
            logger.info(f"Would delete event {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Calendar delete event error: {str(e)}")
            return False
    
    def get_free_busy(
        self,
        start_date: datetime,
        end_date: datetime,
        technician_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get free/busy slots для availability check.
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            technician_id: Optional technician filter
        
        Returns:
            List: Available slots
        """
        service = self._get_service()
        if not service:
            logger.info(f"Would check availability {start_date} to {end_date}")
            return []
        
        try:
            # TODO: Implement freebusy query
            # body = {
            #     'timeMin': start_date.isoformat(),
            #     'timeMax': end_date.isoformat(),
            #     'items': [{'id': calendar_id} for calendar_id in self.calendars.values()]
            # }
            
            # response = service.freebusy().query(body=body).execute()
            
            return []
        
        except Exception as e:
            logger.error(f"Calendar free/busy error: {str(e)}")
            return []
    
    def _format_event_description(self, booking) -> str:
        """Format event description з booking details."""
        description = f"""
        Booking Reference: {booking.booking_reference}
        Service: {booking.service.name}
        Duration: {booking.duration} minutes
        Client: {booking.user.get_full_name()}
        Email: {booking.user.email}
        Phone: {booking.user.phone_number if hasattr(booking.user, 'phone_number') else 'N/A'}
        
        Total: ${booking.final_total}
        Payment Status: {booking.get_payment_status_display()}
        
        Special Requests: {booking.special_requests or 'None'}
        """
        return description.strip()
    
    def _get_attendees(self, booking) -> List[Dict[str, str]]:
        """Get event attendees list."""
        attendees = [
            {'email': booking.user.email, 'displayName': booking.user.get_full_name()}
        ]
        
        if booking.technician and hasattr(booking.technician, 'user'):
            attendees.append({
                'email': booking.technician.user.email,
                'displayName': booking.technician.full_name
            })
        
        return attendees
    
    def _get_calendar_id(self, booking) -> str:
        """Determine which calendar для booking."""
        if booking.service.name.lower().startswith('private'):
            return self.calendars.get('private', self.calendars.get('master'))
        return self.calendars.get('master')


# Global instance
calendar_manager = CalendarManager()

