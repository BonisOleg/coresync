"""
Payments URLs for the CoreSync API.
"""
from django.urls import path
from .stripe_webhooks import stripe_webhook

app_name = 'payments'

urlpatterns = [
    # Stripe webhook - CRITICAL for QuickBooks integration
    path('api/payments/stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    
    # TODO: Add more payment endpoints as needed
    # path('stripe/create-intent/', views.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    # path('quickbooks/callback/', views.QuickBooksCallbackView.as_view(), name='quickbooks_callback'),
]
