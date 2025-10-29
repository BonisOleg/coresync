"""
AI Agent Views - Atlas webhooks and API endpoints.
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import logging
import asyncio

from .models import Conversation, AgentAction, AtlasLog
from .assistant_service import assistant_service
from .atlas_connector import atlas_connector

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def atlas_webhook_view(request):
    """
    Atlas AI webhook endpoint.
    Receives phone call/SMS events from Atlas.
    
    Формат webhook від Atlas (припущення, треба уточнити з Atlas docs):
    {
        "event_type": "conversation.completed",
        "session_id": "atlas_session_123",
        "user_phone": "+15515742281",
        "transcript": [...],
        "intent": "booking_request",
        "extracted_data": {
            "service_type": "massage",
            "preferred_date": "2025-11-15",
            "customer_name": "John Doe",
            "customer_email": "john@example.com"
        }
    }
    
    Security: Verify signature (буде додано коли Atlas API keys готові)
    """
    try:
        # Verify signature
        signature = request.headers.get('X-Atlas-Signature', '')
        
        # FIXME: Uncomment після отримання Atlas credentials
        # if not atlas_connector.verify_webhook_signature(request.body, signature):
        #     logger.warning("Invalid Atlas webhook signature")
        #     return JsonResponse({'error': 'Invalid signature'}, status=403)
        
        # Parse webhook data
        webhook_data = json.loads(request.body.decode('utf-8'))
        
        # Log raw webhook
        atlas_log = AtlasLog.objects.create(
            webhook_data=webhook_data,
            processed=False
        )
        
        # Process webhook асинхронно
        event_type = webhook_data.get('event_type')
        
        if event_type == 'conversation.completed':
            # Conversation завершено, обробляємо результат
            result = asyncio.run(_process_atlas_conversation(webhook_data, atlas_log.id))
            
            return JsonResponse({
                'status': 'processed',
                'log_id': atlas_log.id,
                'result': result
            }, status=200)
        
        elif event_type == 'booking.created':
            # Atlas вже створив booking (якщо така логіка буде)
            result = asyncio.run(_process_atlas_booking(webhook_data, atlas_log.id))
            
            return JsonResponse({
                'status': 'received',
                'log_id': atlas_log.id,
                'result': result
            }, status=200)
        
        else:
            # Unknown event, just log
            logger.info(f"Atlas webhook received (unknown type): {event_type}")
            
            return JsonResponse({
                'status': 'received',
                'log_id': atlas_log.id
            }, status=200)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Atlas webhook")
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)
    
    except Exception as e:
        logger.error(f"Atlas webhook error: {str(e)}")
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)


async def _process_atlas_conversation(webhook_data: dict, log_id: int) -> dict:
    """
    Обробляє завершену розмову від Atlas.
    Якщо є намір на booking - створює бронювання.
    """
    try:
        session_id = webhook_data.get('session_id')
        intent = webhook_data.get('intent')
        extracted_data = webhook_data.get('extracted_data', {})
        
        # Якщо це booking request
        if intent == 'booking_request':
            # Формуємо message для assistant
            message = f"Створити бронювання: {extracted_data.get('service_type')} на {extracted_data.get('preferred_date')}"
            
            # Обробляємо через assistant service
            result = await assistant_service.process_message(
                message=message,
                session_id=f"atlas_{session_id}",
                user_id=None,  # TODO: Match по phone/email
                source='atlas_phone',
                context=extracted_data
            )
            
            # Оновлюємо log
            from asgiref.sync import sync_to_async
            await sync_to_async(
                AtlasLog.objects.filter(id=log_id).update
            )(processed=True, processing_result=result)
            
            logger.info(f"Atlas conversation processed: {session_id}")
            return result
        
        return {'status': 'no_action_required'}
    
    except Exception as e:
        logger.error(f"Error processing Atlas conversation: {str(e)}")
        return {'error': str(e)}


async def _process_atlas_booking(webhook_data: dict, log_id: int) -> dict:
    """
    Обробляє готове бронювання від Atlas.
    Зберігає в нашу систему.
    """
    try:
        # TODO: Implement після з'ясування Atlas booking flow
        logger.info(f"Atlas booking received: {webhook_data}")
        
        return {'status': 'booking_saved'}
    
    except Exception as e:
        logger.error(f"Error processing Atlas booking: {str(e)}")
        return {'error': str(e)}


@api_view(['GET'])
@permission_classes([AllowAny])
def conversation_context_view(request, session_id):
    """
    Get conversation context by session ID.
    Used by frontend to restore conversation state.
    """
    try:
        conversation = Conversation.objects.get(session_id=session_id)
        
        return Response({
            'session_id': str(conversation.session_id),
            'status': conversation.status,
            'context_data': conversation.context_data,
            'user': {
                'email': conversation.user.email if conversation.user else None,
                'is_member': conversation.user.membership_set.exists() if conversation.user else False
            } if conversation.user else None,
            'booking_id': conversation.booking.id if conversation.booking else None,
            'started_at': conversation.started_at.isoformat(),
        })
    
    except Conversation.DoesNotExist:
        return Response({
            'error': 'Conversation not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def conversation_history_view(request, session_id):
    """
    Get conversation message history.
    Returns all actions for replay/display.
    """
    try:
        conversation = Conversation.objects.get(session_id=session_id)
        
        actions = conversation.actions.all()
        history = []
        
        for action in actions:
            history.append({
                'type': action.action_type,
                'query': action.query,
                'response': action.response,
                'timestamp': action.timestamp.isoformat(),
                'metadata': action.metadata
            })
        
        return Response({
            'session_id': str(conversation.session_id),
            'history': history,
            'total_actions': len(history)
        })
    
    except Conversation.DoesNotExist:
        return Response({
            'error': 'Conversation not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def chat_message_view(request):
    """
    Головний endpoint для чату на website/mobile.
    
    Request:
    {
        "message": "Хочу забронювати масаж",
        "session_id": "uuid-session-id",
        "user_id": 123 (optional),
        "source": "web" | "mobile"
    }
    
    Response:
    {
        "response": "текст відповіді",
        "actions": [...],
        "metadata": {...},
        "requires_payment": false
    }
    """
    try:
        message = request.data.get('message')
        session_id = request.data.get('session_id')
        user_id = request.data.get('user_id')
        source = request.data.get('source', 'web')
        context = request.data.get('context', {})
        
        if not message or not session_id:
            return Response({
                'error': 'message and session_id required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process через assistant service
        result = asyncio.run(
            assistant_service.process_message(
                message=message,
                session_id=session_id,
                user_id=user_id,
                source=source,
                context=context
            )
        )
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Chat message error: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def collect_email_view(request):
    """
    Збір email для newsletters.
    
    Request:
    {
        "email": "customer@example.com",
        "source": "chat_bot" | "website_form",
        "consent": true
    }
    """
    try:
        email = request.data.get('email')
        source = request.data.get('source', 'unknown')
        consent = request.data.get('consent', False)
        
        if not email or not consent:
            return Response({
                'error': 'email and consent required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save to newsletter list
        from users.models import User
        
        # Check if user exists
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'newsletter_consent': consent
            }
        )
        
        if not created and not user.newsletter_consent:
            user.newsletter_consent = consent
            user.save(update_fields=['newsletter_consent'])
        
        logger.info(f"Email collected: {email} from {source}")
        
        return Response({
            'status': 'success',
            'message': 'Email added to newsletter list'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Email collection error: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_ai_view(request):
    """
    Test endpoint for development.
    Returns AI agent status.
    """
    return Response({
        'status': 'AI Agent operational',
        'version': '2.0.0',
        'features': [
            '✅ Atlas webhook integration',
            '✅ Universal Assistant Service',
            '✅ Booking orchestration',
            '✅ Multi-channel support (Web, Mobile, Phone)',
            '✅ Payment integration ready',
            '✅ Email collection',
            '✅ Context management',
            '⏳ Atlas credentials (waiting)',
            '⏳ Google Calendar sync (waiting payment card)'
        ],
        'endpoints': {
            'chat': '/api/ai/chat/',
            'atlas_webhook': '/api/ai/atlas/webhook/',
            'email_collect': '/api/ai/collect-email/'
        }
    })
