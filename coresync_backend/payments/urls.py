"""
Payments URLs for the CoreSync API.
"""
from django.urls import path

app_name = 'payments'

urlpatterns = [
    # TODO: Add payment endpoints
    # path('stripe/create-intent/', views.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    # path('stripe/webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    # path('quickbooks/callback/', views.QuickBooksCallbackView.as_view(), name='quickbooks_callback'),
]
