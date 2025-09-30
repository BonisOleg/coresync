"""
Django management command for QuickBooks synchronization.
Usage: python manage.py sync_quickbooks [--type=all|customers|services|payments|invoices]
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from payments.quickbooks_service import quickbooks_service
from payments.models import QuickBooksSync
import sys


class Command(BaseCommand):
    help = 'Synchronize data with QuickBooks API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            choices=['all', 'customers', 'services', 'payments', 'invoices', 'queue'],
            help='Type of data to sync (default: all)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of items to process (default: 50)'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test QuickBooks connection without syncing data'
        )
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Retry failed sync items'
        )

    def handle(self, *args, **options):
        """Main command handler."""
        self.stdout.write(
            self.style.SUCCESS('Starting QuickBooks synchronization...')
        )
        
        # Check if QuickBooks is configured
        if not quickbooks_service.is_configured():
            self.stdout.write(
                self.style.ERROR(
                    'QuickBooks is not configured. Please check your settings:\n'
                    '- QUICKBOOKS_COMPANY_ID\n'
                    '- QUICKBOOKS_CLIENT_ID\n'
                    '- QUICKBOOKS_CLIENT_SECRET\n'
                    '- QUICKBOOKS_ACCESS_TOKEN'
                )
            )
            return

        # Test connection if requested
        if options['test']:
            self._test_connection()
            return

        # Process sync queue if requested
        if options['type'] == 'queue':
            self._process_sync_queue(options['limit'])
            return

        # Retry failed items if requested
        if options['retry_failed']:
            self._retry_failed_syncs(options['limit'])
            return

        # Sync specific data types
        sync_type = options['type']
        limit = options['limit']

        try:
            if sync_type in ['all', 'customers']:
                self._sync_customers(limit)

            if sync_type in ['all', 'services']:
                self._sync_services()

            if sync_type in ['all', 'invoices']:
                self._sync_invoices(limit)

            if sync_type in ['all', 'payments']:
                self._sync_payments(limit)

            self.stdout.write(
                self.style.SUCCESS('✅ QuickBooks synchronization completed successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Synchronization failed: {e}')
            )
            raise CommandError(f'Synchronization failed: {e}')

    def _test_connection(self):
        """Test QuickBooks API connection."""
        self.stdout.write('Testing QuickBooks connection...')
        
        success, message = quickbooks_service.test_connection()
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Connection successful: {message}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Connection failed: {message}')
            )

    def _sync_customers(self, limit):
        """Sync customers to QuickBooks."""
        from users.models import User
        
        self.stdout.write('Syncing customers...')
        
        # Get users who haven't been synced or need updates
        users_to_sync = User.objects.filter(
            is_active=True
        ).exclude(
            id__in=QuickBooksSync.objects.filter(
                sync_type='customer',
                status='completed'
            ).values_list('object_id', flat=True)
        )[:limit]
        
        success_count = 0
        failed_count = 0
        
        for user in users_to_sync:
            try:
                success, qb_id, message = quickbooks_service.sync_customer(user)
                
                if success:
                    success_count += 1
                    self.stdout.write(f'  ✅ {user.email} -> {qb_id}')
                else:
                    failed_count += 1
                    self.stdout.write(f'  ❌ {user.email}: {message}')
                    
            except Exception as e:
                failed_count += 1
                self.stdout.write(f'  ❌ {user.email}: {e}')
        
        self.stdout.write(
            f'Customer sync completed: {success_count} success, {failed_count} failed'
        )

    def _sync_services(self):
        """Sync services to QuickBooks items."""
        self.stdout.write('Syncing services...')
        
        results = quickbooks_service.sync_service_items()
        
        if 'error' in results:
            self.stdout.write(
                self.style.ERROR(f'❌ Service sync failed: {results["error"]}')
            )
        else:
            self.stdout.write(
                f'Service sync completed: {results["success"]} success, '
                f'{results["failed"]} failed, {results["skipped"]} skipped'
            )
            
            if results['errors']:
                for error in results['errors']:
                    self.stdout.write(f'  ❌ {error}')

    def _sync_invoices(self, limit):
        """Sync booking invoices to QuickBooks."""
        from services.booking_models import Booking
        
        self.stdout.write('Syncing invoices...')
        
        # Get bookings that need invoice sync
        bookings_to_sync = Booking.objects.filter(
            status__in=['confirmed', 'completed'],
            quickbooks_synced=False
        ).exclude(
            id__in=QuickBooksSync.objects.filter(
                sync_type='invoice',
                status='completed'
            ).values_list('object_id', flat=True)
        )[:limit]
        
        success_count = 0
        failed_count = 0
        
        for booking in bookings_to_sync:
            try:
                success, qb_id, message = quickbooks_service.sync_booking_invoice(booking)
                
                if success:
                    success_count += 1
                    self.stdout.write(f'  ✅ {booking.booking_reference} -> {qb_id}')
                else:
                    failed_count += 1
                    self.stdout.write(f'  ❌ {booking.booking_reference}: {message}')
                    
            except Exception as e:
                failed_count += 1
                self.stdout.write(f'  ❌ {booking.booking_reference}: {e}')
        
        self.stdout.write(
            f'Invoice sync completed: {success_count} success, {failed_count} failed'
        )

    def _sync_payments(self, limit):
        """Sync payments to QuickBooks."""
        from payments.models import Payment
        
        self.stdout.write('Syncing payments...')
        
        # Get payments that need sync
        payments_to_sync = Payment.objects.filter(
            status='succeeded'
        ).exclude(
            id__in=QuickBooksSync.objects.filter(
                sync_type='payment',
                status='completed'
            ).values_list('object_id', flat=True)
        )[:limit]
        
        success_count = 0
        failed_count = 0
        
        for payment in payments_to_sync:
            try:
                success, qb_id, message = quickbooks_service.sync_payment(payment)
                
                if success:
                    success_count += 1
                    self.stdout.write(f'  ✅ {payment.payment_id} -> {qb_id}')
                else:
                    failed_count += 1
                    self.stdout.write(f'  ❌ {payment.payment_id}: {message}')
                    
            except Exception as e:
                failed_count += 1
                self.stdout.write(f'  ❌ {payment.payment_id}: {e}')
        
        self.stdout.write(
            f'Payment sync completed: {success_count} success, {failed_count} failed'
        )

    def _process_sync_queue(self, limit):
        """Process pending sync queue items."""
        self.stdout.write('Processing sync queue...')
        
        results = quickbooks_service.process_sync_queue(limit)
        
        if 'error' in results:
            self.stdout.write(
                self.style.ERROR(f'❌ Queue processing failed: {results["error"]}')
            )
        else:
            self.stdout.write(
                f'Queue processing completed: {results["processed"]} processed, '
                f'{results["successful"]} successful, {results["failed"]} failed'
            )
            
            if results['errors']:
                for error in results['errors']:
                    self.stdout.write(f'  ❌ {error}')

    def _retry_failed_syncs(self, limit):
        """Retry failed sync items."""
        self.stdout.write('Retrying failed syncs...')
        
        failed_syncs = QuickBooksSync.objects.filter(
            status='failed'
        ).filter(
            attempts__lt=models.F('max_attempts')
        )[:limit]
        
        if not failed_syncs.exists():
            self.stdout.write('No failed syncs to retry.')
            return
        
        retry_count = 0
        for sync_item in failed_syncs:
            # Reset for retry
            sync_item.status = 'pending'
            sync_item.error_message = ''
            sync_item.save()
            retry_count += 1
            
            self.stdout.write(f'  🔄 Reset {sync_item.sync_type} {sync_item.object_id} for retry')
        
        self.stdout.write(f'Reset {retry_count} failed syncs for retry')
        
        # Now process them
        self._process_sync_queue(limit)
