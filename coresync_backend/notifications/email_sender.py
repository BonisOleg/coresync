"""
Email Sender - SendGrid integration wrapper.
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class EmailSender:
    """
    SendGrid email sender wrapper.
    Handles all automated emails.
    """
    
    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    
    def send_booking_confirmation(self, booking, attachment=None) -> Dict[str, Any]:
        """
        Send booking confirmation email.
        
        Args:
            booking: Booking object
            attachment: .ics file (optional)
        
        Returns:
            Dict: {'success': bool, 'message_id': str, 'error': str}
        """
        try:
            context = {
                'booking': booking,
                'user': booking.user,
                'service': booking.service,
                'date': booking.booking_date,
                'time': booking.booking_time,
                'location': '1544 71st Street, Brooklyn, NY',
                'parking_info': 'Street parking available',
                'what_to_bring': 'Comfortable clothing, arrive 10 minutes early'
            }
            
            html_content = render_to_string(
                'emails/booking_confirmation.html',
                context
            )
            text_content = strip_tags(html_content)
            
            return self._send_email(
                to_email=booking.user.email,
                to_name=booking.user.get_full_name(),
                subject=f'Booking Confirmed - {booking.service.name}',
                html_content=html_content,
                text_content=text_content,
                # attachments=[attachment] if attachment else None
            )
        
        except Exception as e:
            logger.error(f"Error sending booking confirmation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_reminder(self, booking) -> Dict[str, Any]:
        """Send 24-hour reminder email."""
        try:
            context = {
                'booking': booking,
                'user': booking.user,
                'service': booking.service,
                'date': booking.booking_date,
                'time': booking.booking_time,
                'location': '1544 71st Street, Brooklyn, NY',
                'directions_url': 'https://maps.google.com/?q=1544+71st+Street+Brooklyn+NY'
            }
            
            html_content = render_to_string(
                'emails/reminder_24hr.html',
                context
            )
            text_content = strip_tags(html_content)
            
            return self._send_email(
                to_email=booking.user.email,
                to_name=booking.user.get_full_name(),
                subject=f'Reminder: Your appointment tomorrow at {booking.booking_time}',
                html_content=html_content,
                text_content=text_content
            )
        
        except Exception as e:
            logger.error(f"Error sending reminder: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_review_request(self, booking) -> Dict[str, Any]:
        """Send review request email."""
        try:
            context = {
                'booking': booking,
                'user': booking.user,
                'service': booking.service,
                'review_url': 'https://g.page/r/YOUR_GOOGLE_BUSINESS_ID/review',  # TODO: Add real URL
                'incentive': 'As a thank you, enjoy 10% off your next booking!'
            }
            
            html_content = render_to_string(
                'emails/review_request.html',
                context
            )
            text_content = strip_tags(html_content)
            
            return self._send_email(
                to_email=booking.user.email,
                to_name=booking.user.get_full_name(),
                subject='How was your CoreSync experience?',
                html_content=html_content,
                text_content=text_content
            )
        
        except Exception as e:
            logger.error(f"Error sending review request: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_membership_welcome(self, user, membership, attachment=None) -> Dict[str, Any]:
        """Send membership welcome email."""
        try:
            context = {
                'user': user,
                'membership': membership,
                'tier': membership.tier,
                'benefits': self._get_tier_benefits(membership.tier),
                'monthly_price': membership.monthly_price,
                'portal_url': 'https://coresync.life/dashboard/'
            }
            
            html_content = render_to_string(
                'emails/membership_welcome.html',
                context
            )
            text_content = strip_tags(html_content)
            
            return self._send_email(
                to_email=user.email,
                to_name=user.get_full_name(),
                subject=f'Welcome to CoreSync {membership.tier.title()} Membership!',
                html_content=html_content,
                text_content=text_content,
                # attachments=[attachment] if attachment else None
            )
        
        except Exception as e:
            logger.error(f"Error sending membership welcome: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: str,
        attachments: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send email через SendGrid API.
        
        TODO: Activate після встановлення sendgrid package.
        """
        if not self.api_key:
            logger.warning("SendGrid API key not configured")
            return {
                'success': False,
                'error': 'SendGrid not configured'
            }
        
        try:
            # TODO: Implement SendGrid API call
            # from sendgrid import SendGridAPIClient
            # from sendgrid.helpers.mail import Mail
            
            # message = Mail(
            #     from_email=self.from_email,
            #     to_emails=to_email,
            #     subject=subject,
            #     html_content=html_content
            # )
            
            # sg = SendGridAPIClient(self.api_key)
            # response = sg.send(message)
            
            # return {
            #     'success': True,
            #     'message_id': response.headers.get('X-Message-Id'),
            #     'status_code': response.status_code
            # }
            
            logger.info(f"Email would be sent to {to_email}: {subject}")
            return {
                'success': True,
                'message_id': 'test-message-id',
                'note': 'SendGrid not yet configured'
            }
        
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_technician_booking_notification(self, booking) -> Dict[str, Any]:
        """
        Send booking notification до technician.
        Повідомляє про нове призначене бронювання.
        """
        try:
            if not booking.technician:
                return {'success': False, 'error': 'No technician assigned'}
            
            context = {
                'booking': booking,
                'technician': booking.technician,
                'client': booking.user,
                'service': booking.service,
                'date': booking.booking_date,
                'time': booking.start_time,
                'end_time': booking.end_time,
                'duration': booking.duration,
                'special_requests': booking.special_requests,
                'location': '1544 71st Street, Brooklyn, NY'
            }
            
            html_content = render_to_string(
                'emails/technician_booking_notification.html',
                context
            )
            text_content = strip_tags(html_content)
            
            return self._send_email(
                to_email=booking.technician.email,
                to_name=booking.technician.full_name,
                subject=f'New Booking Assignment - {booking.service.name}',
                html_content=html_content,
                text_content=text_content
            )
        
        except Exception as e:
            logger.error(f"Error sending technician notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_tier_benefits(self, tier: str) -> list:
        """Get benefits list для membership tier."""
        benefits = {
            'base': [
                '25-30% discount на всі послуги',
                'AI Massage discounted',
                'Backyard bookable',
                'Priority booking 2-3 місяці вперед'
            ],
            'premium': [
                '1-2 безкоштовні процедури щомісяця',
                '30-40% знижка на додаткові послуги',
                '1 безкоштовний AI Massage щомісяця',
                'Coresync Private discounted',
                'Birthday perk'
            ],
            'unlimited': [
                'Всі послуги включено',
                'Unlimited AI Massage',
                'Unlimited Coresync Private',
                'Unlimited Backyard',
                'Exclusive concierge service'
            ]
        }
        return benefits.get(tier, [])

