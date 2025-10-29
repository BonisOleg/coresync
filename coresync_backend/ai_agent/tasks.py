"""
AI Agent Celery Tasks - Async background processing.
"""
from celery import shared_task
import logging
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='ai_agent.tasks.process_atlas_webhook')
def process_atlas_webhook(atlas_log_id: int):
    """
    Process Atlas AI webhook asynchronously.
    
    Args:
        atlas_log_id: ID AtlasLog record
    
    TODO: Activate після Atlas API keys.
    """
    try:
        from .models import AtlasLog, Conversation
        
        atlas_log = AtlasLog.objects.get(id=atlas_log_id)
        webhook_data = atlas_log.webhook_data
        
        # Extract data from webhook
        event_type = webhook_data.get('event_type')
        session_id = webhook_data.get('session_id')
        message = webhook_data.get('message', {}).get('text', '')
        
        logger.info(f"Processing Atlas webhook: {event_type}")
        
        # Create або update conversation
        # TODO: Implement Atlas-specific logic
        
        # Mark log as processed
        atlas_log.mark_processed()
        
        return {
            'status': 'success',
            'atlas_log_id': atlas_log_id,
            'event_type': event_type
        }
    
    except Exception as e:
        logger.error(f"Error processing Atlas webhook: {str(e)}")
        
        # Update error message
        try:
            atlas_log = AtlasLog.objects.get(id=atlas_log_id)
            atlas_log.error_message = str(e)
            atlas_log.save(update_fields=['error_message'])
        except:
            pass
        
        raise


@shared_task(name='ai_agent.tasks.cleanup_old_conversations')
def cleanup_old_conversations():
    """
    Cleanup старі conversation records (>30 days).
    Runs daily at 3 AM EST (згідно celery beat schedule).
    """
    try:
        from .models import Conversation, AgentAction
        
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Delete old conversations
        old_conversations = Conversation.objects.filter(
            started_at__lt=cutoff_date,
            status__in=['completed', 'abandoned', 'error']
        )
        
        count = old_conversations.count()
        
        # Delete related actions (cascade)
        old_conversations.delete()
        
        logger.info(f"Cleaned up {count} old conversations")
        
        return {
            'status': 'success',
            'deleted_count': count,
            'cutoff_date': cutoff_date.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error cleaning up conversations: {str(e)}")
        raise


@shared_task(name='ai_agent.tasks.log_conversation_analytics')
def log_conversation_analytics(session_id: str):
    """
    Export conversation analytics до BigQuery/Google Sheets.
    
    Args:
        session_id: UUID сесії для експорту
    
    TODO: Phase 2 - implement analytics export.
    """
    try:
        from .models import Conversation
        
        conversation = Conversation.objects.get(session_id=session_id)
        
        # Calculate metrics
        actions_count = conversation.actions.count()
        duration = conversation.duration_minutes
        
        analytics_data = {
            'session_id': str(session_id),
            'source': conversation.source,
            'status': conversation.status,
            'actions_count': actions_count,
            'duration_minutes': duration,
            'has_booking': conversation.booking is not None,
            'user_id': conversation.user.id if conversation.user else None,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(f"Analytics logged for {session_id}")
        
        # TODO: Export до Google Sheets/BigQuery
        
        return analytics_data
    
    except Exception as e:
        logger.error(f"Error logging analytics: {str(e)}")
        raise


@shared_task(name='ai_agent.tasks.send_conversation_summary')
def send_conversation_summary(session_id: str, recipient_email: str):
    """
    Send conversation summary email до користувача.
    
    Args:
        session_id: UUID сесії
        recipient_email: Email отримувача
    
    TODO: Integrate з notifications app.
    """
    try:
        from .models import Conversation
        
        conversation = Conversation.objects.get(session_id=session_id)
        actions = conversation.actions.order_by('timestamp')
        
        # Generate summary
        summary_lines = []
        for action in actions:
            if action.action_type == 'user_message':
                summary_lines.append(f"User: {action.query}")
            elif action.action_type == 'agent_response':
                summary_lines.append(f"AI: {action.response}")
        
        summary_text = "\n".join(summary_lines)
        
        logger.info(f"Sending summary for {session_id} to {recipient_email}")
        
        # TODO: Send email через notifications.tasks
        
        return {
            'status': 'success',
            'session_id': str(session_id),
            'recipient': recipient_email
        }
    
    except Exception as e:
        logger.error(f"Error sending summary: {str(e)}")
        raise

