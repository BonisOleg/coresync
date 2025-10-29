"""
AI Agent URL Configuration.
"""
from django.urls import path
from . import views

app_name = 'ai_agent'

urlpatterns = [
    # ========== MAIN ENDPOINTS ==========
    
    # Chat API - для website та mobile (POST)
    path('chat/', views.chat_message_view, name='chat_message'),
    
    # Email collection для newsletters (POST)
    path('collect-email/', views.collect_email_view, name='collect_email'),
    
    # ========== ATLAS INTEGRATION ==========
    
    # Atlas webhook endpoint (POST)
    path('atlas/webhook/', views.atlas_webhook_view, name='atlas_webhook'),
    
    # ========== CONVERSATION MANAGEMENT ==========
    
    # Conversation context API (GET)
    path('context/<uuid:session_id>/', views.conversation_context_view, name='conversation_context'),
    
    # Chat history API (GET)
    path('history/<uuid:session_id>/', views.conversation_history_view, name='conversation_history'),
    
    # ========== UTILITY ==========
    
    # Test endpoint (development only)
    path('test/', views.test_ai_view, name='test_ai'),
]

# WebSocket routing (буде додано в config/asgi.py при необхідності)

