"""
AI Agent Core Logic - Async conversation management.
Handles intent detection, context tracking, response generation.
"""
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from django.utils import timezone

from .models import Conversation, AgentAction
from .context_manager import ContextManager
from .intent_classifier import IntentClassifier

logger = logging.getLogger(__name__)


class AIAgentCore:
    """
    Core AI agent logic для обробки розмов.
    Async conversation handler з multithreading support.
    """
    
    def __init__(self):
        self.context_manager = ContextManager()
        self.intent_classifier = IntentClassifier()
        self.response_templates = self._load_response_templates()
    
    def _load_response_templates(self) -> Dict[str, Any]:
        """Load response templates from JSON file."""
        try:
            # TODO: Create response_templates.json
            return {
                'greeting': "Привіт! Я AI асистент CoreSync. Як я можу вам допомогти?",
                'booking_intent': "Чудово! Я допоможу забронювати процедуру. Який тип сервісу вас цікавить?",
                'pricing_request': "Ціни залежать від вашого membership tier. Чи є у вас membership?",
                'availability': "Перевіряю доступні слоти...",
                'error': "Вибачте, виникла помилка. Спробуйте ще раз.",
                'fallback': "Не зовсім зрозумів. Можете перефразувати?"
            }
        except Exception as e:
            logger.error(f"Failed to load response templates: {str(e)}")
            return {}
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str,
        user_id: Optional[int] = None,
        source: str = 'web_chat'
    ) -> Dict[str, Any]:
        """
        Process user message асинхронно.
        
        Args:
            session_id: UUID сесії розмови
            user_message: Текст повідомлення від користувача
            user_id: ID користувача (якщо authenticated)
            source: Джерело (web_chat, atlas_phone, atlas_sms)
        
        Returns:
            Dict з response, metadata, next_action
        """
        start_time = datetime.now()
        
        try:
            # Get або create conversation
            conversation = await self._get_or_create_conversation(
                session_id, user_id, source
            )
            
            # Load context
            context = await self.context_manager.get_context(session_id)
            
            # Log user message
            await self._log_action(
                conversation=conversation,
                action_type='user_message',
                query=user_message,
                response=''
            )
            
            # Classify intent
            intent = await self.intent_classifier.classify(
                message=user_message,
                context=context
            )
            
            # Generate response based on intent
            response_data = await self._generate_response(
                intent=intent,
                context=context,
                conversation=conversation
            )
            
            # Update context
            updated_context = await self._update_context(
                session_id=session_id,
                old_context=context,
                intent=intent,
                user_message=user_message,
                response=response_data['response']
            )
            
            # Log agent response
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            await self._log_action(
                conversation=conversation,
                action_type='agent_response',
                query='',
                response=response_data['response'],
                metadata={
                    'intent': intent['type'],
                    'confidence': intent['confidence']
                },
                processing_time_ms=int(processing_time)
            )
            
            return {
                'session_id': str(session_id),
                'response': response_data['response'],
                'intent': intent,
                'context': updated_context,
                'next_action': response_data.get('next_action'),
                'processing_time_ms': int(processing_time)
            }
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                'session_id': str(session_id),
                'response': self.response_templates.get('error'),
                'error': str(e)
            }
    
    async def _get_or_create_conversation(
        self, 
        session_id: str, 
        user_id: Optional[int], 
        source: str
    ) -> Conversation:
        """Get existing або create new conversation."""
        try:
            # Django ORM async wrapper (Django 4.1+)
            from asgiref.sync import sync_to_async
            
            get_conv = sync_to_async(
                Conversation.objects.get,
                thread_sensitive=True
            )
            create_conv = sync_to_async(
                Conversation.objects.create,
                thread_sensitive=True
            )
            
            try:
                return await get_conv(session_id=session_id)
            except Conversation.DoesNotExist:
                return await create_conv(
                    session_id=session_id,
                    user_id=user_id,
                    source=source,
                    status='active'
                )
        
        except Exception as e:
            logger.error(f"Error getting/creating conversation: {str(e)}")
            raise
    
    async def _log_action(
        self,
        conversation: Conversation,
        action_type: str,
        query: str,
        response: str,
        metadata: Optional[Dict] = None,
        processing_time_ms: Optional[int] = None
    ):
        """Log action to database асинхронно."""
        try:
            from asgiref.sync import sync_to_async
            
            create_action = sync_to_async(
                AgentAction.objects.create,
                thread_sensitive=True
            )
            
            await create_action(
                conversation=conversation,
                action_type=action_type,
                query=query,
                response=response,
                metadata=metadata or {},
                processing_time_ms=processing_time_ms
            )
        
        except Exception as e:
            logger.error(f"Error logging action: {str(e)}")
    
    async def _generate_response(
        self,
        intent: Dict[str, Any],
        context: Dict[str, Any],
        conversation: Conversation
    ) -> Dict[str, Any]:
        """
        Generate response based on intent and context.
        
        TODO: Implement sophisticated response generation.
        Phase 2: Integrate з booking_orchestrator, pricing_engine
        """
        intent_type = intent.get('type', 'unknown')
        
        # Simple template-based responses (Phase 1)
        response_text = self.response_templates.get(
            intent_type,
            self.response_templates.get('fallback')
        )
        
        return {
            'response': response_text,
            'next_action': self._determine_next_action(intent_type)
        }
    
    def _determine_next_action(self, intent_type: str) -> Optional[str]:
        """Determine next action based on intent."""
        action_mapping = {
            'booking_intent': 'show_services',
            'pricing_request': 'check_membership',
            'availability': 'check_calendar',
            'payment': 'process_payment'
        }
        return action_mapping.get(intent_type)
    
    async def _update_context(
        self,
        session_id: str,
        old_context: Dict[str, Any],
        intent: Dict[str, Any],
        user_message: str,
        response: str
    ) -> Dict[str, Any]:
        """Update conversation context."""
        updated_context = {
            **old_context,
            'last_intent': intent['type'],
            'last_user_message': user_message,
            'last_response': response,
            'message_count': old_context.get('message_count', 0) + 1,
            'updated_at': timezone.now().isoformat()
        }
        
        await self.context_manager.set_context(session_id, updated_context)
        return updated_context


# Example usage
async def example_usage():
    """Example of using AIAgentCore."""
    agent = AIAgentCore()
    
    result = await agent.process_message(
        session_id='test-session-123',
        user_message='Привіт! Хочу забронювати масаж.',
        user_id=None,
        source='web_chat'
    )
    
    print(f"Response: {result['response']}")
    print(f"Intent: {result['intent']}")
    print(f"Processing time: {result['processing_time_ms']}ms")


if __name__ == '__main__':
    asyncio.run(example_usage())

