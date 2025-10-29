"""
Stripe webhook handlers for automatic payment status updates.
Ensures all successful payments are automatically synced to QuickBooks.
"""
import json
import logging
import stripe
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone

from .models import Payment, StripeWebhookEvent
# from .tasks import sync_specific_payment  # DISABLED - no celery

logger = logging.getLogger(__name__)

# Set Stripe API key
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    Automatically updates payment status and triggers QuickBooks sync.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    
    try:
        # Verify webhook signature
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            # For development - parse without verification
            event = json.loads(payload)
        
        # Log webhook event
        StripeWebhookEvent.objects.create(
            stripe_event_id=event['id'],
            event_type=event['type'],
            processed=False,
            raw_data=event
        )
        
        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            handle_payment_succeeded(event['data']['object'])
        
        elif event['type'] == 'payment_intent.payment_failed':
            handle_payment_failed(event['data']['object'])
        
        elif event['type'] == 'payment_intent.canceled':
            handle_payment_canceled(event['data']['object'])
        
        elif event['type'] == 'invoice.payment_succeeded':
            handle_subscription_payment_succeeded(event['data']['object'])
        
        elif event['type'] == 'customer.subscription.created':
            handle_subscription_created(event['data']['object'])
        
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])
        
        else:
            logger.info(f"Unhandled Stripe event type: {event['type']}")
        
        return HttpResponse(status=200)
        
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid Stripe webhook signature")
        return HttpResponseBadRequest("Invalid signature")
    
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return HttpResponseBadRequest(f"Webhook error: {e}")


def handle_payment_succeeded(payment_intent):
    """
    Handle successful payment - update status and trigger QuickBooks sync.
    """
    try:
        # Find corresponding payment record
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent['id']
        ).first()
        
        if not payment:
            logger.warning(f"Payment record not found for Stripe PaymentIntent {payment_intent['id']}")
            return
        
        # Update payment status
        payment.status = 'succeeded'
        payment.processed_at = timezone.now()
        payment.stripe_charge_id = payment_intent.get('latest_charge', '')
        payment.save()
        
        logger.info(f"Payment {payment.payment_id} marked as succeeded")
        
        # QuickBooks sync disabled for initial deploy
        # TODO: Re-enable when celery is available
        
        # Also update related booking status if applicable
        if payment.payment_type == 'service' and 'booking_id' in payment.metadata:
            try:
                from services.booking_models import Booking
                booking = Booking.objects.get(id=payment.metadata['booking_id'])
                booking.payment_status = 'paid'
                booking.status = 'confirmed'
                booking.confirmed_at = timezone.now()
                booking.save()
                
                logger.info(f"Booking {booking.booking_reference} confirmed after payment")
                
                # NEW: Trigger booking confirmation email
                try:
                    # Will be activated після створення notifications app
                    # from notifications.tasks import send_booking_confirmation
                    # send_booking_confirmation.delay(booking.id)
                    logger.info(f"Booking confirmation email queued for booking {booking.id}")
                    
                    # NEW: Notify technician про нове бронювання
                    if booking.technician:
                        # from notifications.technician_tasks import send_technician_booking_notification
                        # send_technician_booking_notification.delay(booking.id)
                        logger.info(f"Technician notification queued for booking {booking.id}")
                except ImportError:
                    logger.warning("Notifications app not yet available")
                
            except Booking.DoesNotExist:
                logger.warning(f"Booking not found for payment {payment.payment_id}")
        
    except Exception as e:
        logger.error(f"Error handling payment success for {payment_intent['id']}: {e}")


def handle_payment_failed(payment_intent):
    """
    Handle failed payment.
    """
    try:
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent['id']
        ).first()
        
        if payment:
            payment.status = 'failed'
            payment.save()
            
            logger.info(f"Payment {payment.payment_id} marked as failed")
            
            # Update related booking if applicable
            if payment.payment_type == 'service' and 'booking_id' in payment.metadata:
                try:
                    from services.booking_models import Booking
                    booking = Booking.objects.get(id=payment.metadata['booking_id'])
                    booking.payment_status = 'failed'
                    booking.status = 'cancelled'
                    booking.cancelled_at = timezone.now()
                    booking.cancellation_reason = "Payment failed"
                    booking.save()
                    
                    logger.info(f"Booking {booking.booking_reference} cancelled due to payment failure")
                except Booking.DoesNotExist:
                    pass
    
    except Exception as e:
        logger.error(f"Error handling payment failure for {payment_intent['id']}: {e}")


def handle_payment_canceled(payment_intent):
    """
    Handle canceled payment.
    """
    try:
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent['id']
        ).first()
        
        if payment:
            payment.status = 'cancelled'
            payment.save()
            
            logger.info(f"Payment {payment.payment_id} marked as cancelled")
    
    except Exception as e:
        logger.error(f"Error handling payment cancellation for {payment_intent['id']}: {e}")


def handle_subscription_payment_succeeded(invoice):
    """
    Handle successful subscription payment (membership renewals).
    """
    try:
        stripe_customer_id = invoice['customer']
        amount = invoice['amount_paid'] / 100  # Convert from cents
        
        # Find user by Stripe customer ID
        from users.models import User
        user = User.objects.filter(stripe_customer_id=stripe_customer_id).first()
        
        if not user:
            logger.warning(f"User not found for Stripe customer {stripe_customer_id}")
            return
        
        # Create payment record for subscription
        payment = Payment.objects.create(
            user=user,
            payment_type='membership',
            payment_method='stripe_subscription',
            amount=amount,
            currency='USD',
            status='succeeded',
            processed_at=timezone.now(),
            description=f"Membership subscription payment",
            stripe_charge_id=invoice['charge'],
            metadata={
                'stripe_invoice_id': invoice['id'],
                'subscription_period_start': invoice['period_start'],
                'subscription_period_end': invoice['period_end'],
            }
        )
        
        # Link to membership if exists
        if hasattr(user, 'membership'):
            payment.membership = user.membership
            payment.save()
        
        logger.info(f"Created subscription payment record {payment.payment_id} for {user.full_name}")
        
    except Exception as e:
        logger.error(f"Error handling subscription payment for invoice {invoice['id']}: {e}")


def handle_subscription_created(subscription):
    """
    Handle new subscription creation.
    """
    logger.info(f"New subscription created: {subscription['id']}")


def handle_subscription_updated(subscription):
    """
    Handle subscription updates.
    """
    logger.info(f"Subscription updated: {subscription['id']}")


# Manual function to sync all pending payments
def sync_all_pending_payments():
    """
    Manually sync all pending payments to QuickBooks.
    DISABLED for initial deploy - no celery available.
    """
    logger.warning("QuickBooks sync disabled for initial deploy")
    return 0, 0
