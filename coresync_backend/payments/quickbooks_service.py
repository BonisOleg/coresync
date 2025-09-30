"""
QuickBooks API integration service for CoreSync.
Handles synchronization of payments, customers, and invoices.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand

try:
    from quickbooks import QuickBooks
    from quickbooks.objects import Customer, Item, Invoice, Payment, CompanyInfo
    from quickbooks.exceptions import QuickbooksException
    QUICKBOOKS_AVAILABLE = True
except ImportError:
    # Fallback for deployment without QuickBooks libraries
    QUICKBOOKS_AVAILABLE = False
    QuickBooks = None
    Customer = Item = Invoice = Payment = CompanyInfo = None
    QuickbooksException = Exception

from .models import Payment as CoreSyncPayment, QuickBooksSync
from memberships.models import Membership
from services.booking_models import Booking
from users.models import User


logger = logging.getLogger(__name__)


class QuickBooksService:
    """
    Service class for QuickBooks API integration.
    """
    
    def __init__(self):
        self.client = None
        self.company_id = getattr(settings, 'QUICKBOOKS_COMPANY_ID', None)
        self.client_id = getattr(settings, 'QUICKBOOKS_CLIENT_ID', None)
        self.client_secret = getattr(settings, 'QUICKBOOKS_CLIENT_SECRET', None)
        self.access_token = getattr(settings, 'QUICKBOOKS_ACCESS_TOKEN', None)
        self.refresh_token = getattr(settings, 'QUICKBOOKS_REFRESH_TOKEN', None)
        self.sandbox = getattr(settings, 'QUICKBOOKS_SANDBOX', True)
        
        if self.is_configured():
            self._initialize_client()
    
    def is_configured(self):
        """Check if QuickBooks integration is properly configured."""
        if not QUICKBOOKS_AVAILABLE:
            return False
        required_settings = [
            self.company_id,
            self.client_id, 
            self.client_secret,
            self.access_token
        ]
        return all(required_settings)
    
    def _initialize_client(self):
        """Initialize QuickBooks client."""
        if not QUICKBOOKS_AVAILABLE:
            logger.warning("QuickBooks libraries not available - running in compatibility mode")
            self.client = None
            return
            
        try:
            self.client = QuickBooks(
                sandbox=self.sandbox,
                consumer_key=self.client_id,
                consumer_secret=self.client_secret,
                access_token=self.access_token,
                access_token_secret='',  # Not used in OAuth 2.0
                company_id=self.company_id
            )
            logger.info("QuickBooks client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize QuickBooks client: {e}")
            self.client = None
    
    def test_connection(self):
        """Test QuickBooks API connection."""
        if not self.client:
            return False, "Client not initialized"
        
        try:
            company_info = CompanyInfo.all(qb=self.client)
            if company_info:
                return True, f"Connected to: {company_info[0].CompanyName}"
            return False, "No company info found"
        except Exception as e:
            return False, f"Connection test failed: {e}"
    
    def sync_customer(self, user):
        """
        Sync CoreSync user to QuickBooks customer.
        
        Args:
            user: User instance
            
        Returns:
            tuple: (success: bool, qb_customer_id: str, message: str)
        """
        if not self.client:
            return False, None, "QuickBooks client not configured"
        
        sync_record = None
        try:
            # Check if customer already exists in QuickBooks
            sync_record, created = QuickBooksSync.objects.get_or_create(
                sync_type='customer',
                object_id=str(user.id),
                defaults={'status': 'pending'}
            )
            
            sync_record.status = 'in_progress'
            sync_record.attempts += 1
            sync_record.last_attempt_at = timezone.now()
            sync_record.save()
            
            # Search for existing customer by email
            existing_customers = Customer.filter(
                Email=user.email,
                qb=self.client
            )
            
            if existing_customers:
                # Update existing customer
                qb_customer = existing_customers[0]
                qb_customer.Name = user.full_name
                qb_customer.GivenName = user.first_name
                qb_customer.FamilyName = user.last_name
                qb_customer.PrimaryPhone = getattr(user, 'phone', '') if hasattr(user, 'phone') else ''
            else:
                # Create new customer
                qb_customer = Customer()
                qb_customer.Name = user.full_name
                qb_customer.GivenName = user.first_name
                qb_customer.FamilyName = user.last_name
                qb_customer.CompanyName = getattr(user, 'company', '') if hasattr(user, 'company') else ''
                qb_customer.PrimaryEmailAddr = user.email
                qb_customer.PrimaryPhone = getattr(user, 'phone', '') if hasattr(user, 'phone') else ''
            
            # Add membership info to notes
            if hasattr(user, 'membership') and user.membership.is_active:
                membership = user.membership
                qb_customer.Notes = f"CoreSync Member - {membership.plan.name} (Active until {membership.end_date})"
            else:
                qb_customer.Notes = "CoreSync Non-Member"
            
            # Save to QuickBooks
            qb_customer.save(qb=self.client)
            
            # Update sync record
            sync_record.quickbooks_id = str(qb_customer.Id)
            sync_record.status = 'completed'
            sync_record.sync_data.update({
                'qb_customer_name': qb_customer.Name,
                'synced_at': timezone.now().isoformat(),
                'membership_status': 'member' if hasattr(user, 'membership') and user.membership.is_active else 'non_member'
            })
            sync_record.save()
            
            logger.info(f"Successfully synced customer {user.email} to QuickBooks (ID: {qb_customer.Id})")
            return True, str(qb_customer.Id), "Customer synced successfully"
            
        except QuickbooksException as e:
            error_msg = f"QuickBooks API error: {e}"
            logger.error(f"Failed to sync customer {user.email}: {error_msg}")
            
            if sync_record:
                sync_record.status = 'failed'
                sync_record.error_message = error_msg
                sync_record.save()
            
            return False, None, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(f"Failed to sync customer {user.email}: {error_msg}")
            
            if sync_record:
                sync_record.status = 'failed'
                sync_record.error_message = error_msg
                sync_record.save()
            
            return False, None, error_msg
    
    def sync_service_items(self):
        """
        Sync CoreSync services to QuickBooks items.
        
        Returns:
            dict: Results summary
        """
        if not self.client:
            return {'error': 'QuickBooks client not configured'}
        
        from services.models import Service
        
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        services = Service.objects.filter(is_active=True)
        
        for service in services:
            try:
                sync_record, created = QuickBooksSync.objects.get_or_create(
                    sync_type='service',
                    object_id=str(service.id),
                    defaults={'status': 'pending'}
                )
                
                # Skip if already synced and not outdated
                if not created and sync_record.status == 'completed':
                    if sync_record.updated_at > service.updated_at:
                        results['skipped'] += 1
                        continue
                
                sync_record.status = 'in_progress'
                sync_record.attempts += 1
                sync_record.last_attempt_at = timezone.now()
                sync_record.save()
                
                # Create or update QuickBooks item
                qb_item = Item()
                qb_item.Name = service.name
                qb_item.Description = service.short_description or service.description
                qb_item.Type = 'Service'
                qb_item.QtyOnHand = 999  # Services are typically unlimited
                qb_item.UnitPrice = float(service.non_member_price)  # Default to non-member price
                qb_item.IncomeAccountRef = self._get_income_account_ref()
                qb_item.TrackQtyOnHand = False  # Services don't track quantity
                
                # Save to QuickBooks
                qb_item.save(qb=self.client)
                
                # Update sync record
                sync_record.quickbooks_id = str(qb_item.Id)
                sync_record.status = 'completed'
                sync_record.sync_data = {
                    'qb_item_name': qb_item.Name,
                    'member_price': str(service.member_price),
                    'non_member_price': str(service.non_member_price),
                    'synced_at': timezone.now().isoformat()
                }
                sync_record.save()
                
                results['success'] += 1
                logger.info(f"Successfully synced service {service.name} to QuickBooks")
                
            except Exception as e:
                error_msg = f"Failed to sync service {service.name}: {e}"
                results['errors'].append(error_msg)
                results['failed'] += 1
                logger.error(error_msg)
                
                if sync_record:
                    sync_record.status = 'failed'
                    sync_record.error_message = str(e)
                    sync_record.save()
        
        return results
    
    def sync_booking_invoice(self, booking):
        """
        Create/update invoice in QuickBooks for a booking.
        
        Args:
            booking: Booking instance
            
        Returns:
            tuple: (success: bool, qb_invoice_id: str, message: str)
        """
        if not self.client:
            return False, None, "QuickBooks client not configured"
        
        sync_record = None
        try:
            # Ensure customer is synced first
            customer_success, qb_customer_id, _ = self.sync_customer(booking.user)
            if not customer_success:
                return False, None, "Failed to sync customer first"
            
            # Get or create sync record
            sync_record, created = QuickBooksSync.objects.get_or_create(
                sync_type='invoice',
                object_id=str(booking.id),
                defaults={'status': 'pending'}
            )
            
            sync_record.status = 'in_progress'
            sync_record.attempts += 1
            sync_record.last_attempt_at = timezone.now()
            sync_record.save()
            
            # Create QuickBooks invoice
            qb_invoice = Invoice()
            qb_invoice.CustomerRef = qb_customer_id
            qb_invoice.TxnDate = booking.booking_date.isoformat()
            qb_invoice.DueDate = booking.booking_date.isoformat()  # Due same day
            
            # Create invoice lines
            lines = []
            
            # Main service line
            service_line = {
                'Amount': float(booking.base_price),
                'DetailType': 'SalesItemLineDetail',
                'SalesItemLineDetail': {
                    'ItemRef': {'value': self._get_or_create_service_item(booking.service)},
                    'Qty': 1,
                    'UnitPrice': float(booking.base_price)
                }
            }
            lines.append(service_line)
            
            # Add-on lines
            for booking_addon in booking.booking_addons.all():
                addon_line = {
                    'Amount': float(booking_addon.total_price),
                    'DetailType': 'SalesItemLineDetail',
                    'SalesItemLineDetail': {
                        'ItemRef': {'value': self._get_or_create_addon_item(booking_addon.addon)},
                        'Qty': booking_addon.quantity,
                        'UnitPrice': float(booking_addon.unit_price)
                    }
                }
                lines.append(addon_line)
            
            # Discount line (if applicable)
            if booking.discount_applied > 0:
                discount_line = {
                    'Amount': -float(booking.discount_applied),
                    'DetailType': 'SalesItemLineDetail',
                    'SalesItemLineDetail': {
                        'ItemRef': {'value': self._get_discount_item_ref()},
                        'Qty': 1,
                        'UnitPrice': -float(booking.discount_applied)
                    }
                }
                lines.append(discount_line)
            
            qb_invoice.Line = lines
            
            # Add custom fields/memo
            qb_invoice.PrivateNote = f"Booking: {booking.booking_reference}"
            qb_invoice.CustomerMemo = f"Service: {booking.service.name} on {booking.booking_date}"
            
            # Save to QuickBooks
            qb_invoice.save(qb=self.client)
            
            # Update booking
            booking.quickbooks_synced = True
            booking.quickbooks_invoice_id = str(qb_invoice.Id)
            booking.save()
            
            # Update sync record
            sync_record.quickbooks_id = str(qb_invoice.Id)
            sync_record.status = 'completed'
            sync_record.sync_data = {
                'invoice_number': qb_invoice.DocNumber,
                'total_amount': str(booking.final_total),
                'customer_id': qb_customer_id,
                'synced_at': timezone.now().isoformat()
            }
            sync_record.save()
            
            logger.info(f"Successfully created QuickBooks invoice for booking {booking.booking_reference}")
            return True, str(qb_invoice.Id), "Invoice created successfully"
            
        except Exception as e:
            error_msg = f"Failed to create invoice for booking {booking.booking_reference}: {e}"
            logger.error(error_msg)
            
            if sync_record:
                sync_record.status = 'failed'
                sync_record.error_message = error_msg
                sync_record.save()
            
            return False, None, error_msg
    
    def sync_payment(self, payment):
        """
        Sync CoreSync payment to QuickBooks.
        
        Args:
            payment: CoreSyncPayment instance
            
        Returns:
            tuple: (success: bool, qb_payment_id: str, message: str)
        """
        if not self.client:
            return False, None, "QuickBooks client not configured"
        
        sync_record = None
        try:
            # Get sync record
            sync_record, created = QuickBooksSync.objects.get_or_create(
                sync_type='payment',
                object_id=str(payment.id),
                defaults={'status': 'pending'}
            )
            
            sync_record.status = 'in_progress'
            sync_record.attempts += 1
            sync_record.last_attempt_at = timezone.now()
            sync_record.save()
            
            # Ensure customer is synced
            customer_success, qb_customer_id, _ = self.sync_customer(payment.user)
            if not customer_success:
                return False, None, "Failed to sync customer first"
            
            # Create QuickBooks payment
            qb_payment = Payment()
            qb_payment.CustomerRef = qb_customer_id
            qb_payment.TotalAmt = float(payment.amount)
            qb_payment.TxnDate = payment.processed_at.date() if payment.processed_at else payment.created_at.date()
            
            # Set payment method
            payment_method_map = {
                'stripe_card': 'Credit Card',
                'stripe_apple_pay': 'Credit Card',
                'stripe_google_pay': 'Credit Card',
                'cash': 'Cash',
                'check': 'Check',
            }
            qb_payment.PaymentMethodRef = payment_method_map.get(payment.payment_method, 'Other')
            
            # Add reference number
            qb_payment.PrivateNote = f"CoreSync Payment ID: {payment.payment_id}"
            
            # Save to QuickBooks
            qb_payment.save(qb=self.client)
            
            # Update sync record
            sync_record.quickbooks_id = str(qb_payment.Id)
            sync_record.status = 'completed'
            sync_record.sync_data = {
                'payment_amount': str(payment.amount),
                'payment_method': payment.payment_method,
                'customer_id': qb_customer_id,
                'synced_at': timezone.now().isoformat()
            }
            sync_record.save()
            
            logger.info(f"Successfully synced payment {payment.payment_id} to QuickBooks")
            return True, str(qb_payment.Id), "Payment synced successfully"
            
        except Exception as e:
            error_msg = f"Failed to sync payment {payment.payment_id}: {e}"
            logger.error(error_msg)
            
            if sync_record:
                sync_record.status = 'failed'
                sync_record.error_message = error_msg
                sync_record.save()
            
            return False, None, error_msg
    
    def process_sync_queue(self, max_items=50):
        """
        Process pending QuickBooks sync items.
        
        Args:
            max_items: Maximum number of items to process
            
        Returns:
            dict: Processing results
        """
        if not self.client:
            return {'error': 'QuickBooks client not configured'}
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # Get pending sync items
        pending_syncs = QuickBooksSync.objects.filter(
            status__in=['pending', 'failed'],
            attempts__lt=models.F('max_attempts')
        ).order_by('created_at')[:max_items]
        
        for sync_item in pending_syncs:
            results['processed'] += 1
            
            try:
                if sync_item.sync_type == 'customer':
                    user = User.objects.get(id=sync_item.object_id)
                    success, _, _ = self.sync_customer(user)
                
                elif sync_item.sync_type == 'invoice':
                    booking = Booking.objects.get(id=sync_item.object_id)
                    success, _, _ = self.sync_booking_invoice(booking)
                
                elif sync_item.sync_type == 'payment':
                    payment = CoreSyncPayment.objects.get(id=sync_item.object_id)
                    success, _, _ = self.sync_payment(payment)
                
                else:
                    success = False
                    results['errors'].append(f"Unknown sync type: {sync_item.sync_type}")
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                error_msg = f"Failed to process sync {sync_item.id}: {e}"
                results['errors'].append(error_msg)
                results['failed'] += 1
                logger.error(error_msg)
        
        return results
    
    def _get_income_account_ref(self):
        """Get the income account reference for services."""
        # This should be configured based on your QuickBooks setup
        return {'value': '1'}  # Default income account
    
    def _get_or_create_service_item(self, service):
        """Get or create QuickBooks item for service."""
        # Implementation depends on your QuickBooks setup
        return '1'  # Placeholder
    
    def _get_or_create_addon_item(self, addon):
        """Get or create QuickBooks item for add-on."""
        # Implementation depends on your QuickBooks setup
        return '2'  # Placeholder
    
    def _get_discount_item_ref(self):
        """Get the discount item reference."""
        return {'value': '3'}  # Placeholder for discount item


# Singleton instance
quickbooks_service = QuickBooksService()
