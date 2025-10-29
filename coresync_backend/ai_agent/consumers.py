"""
WebSocket Consumer для AI Chat (Django Channels).
Real-time chat handling з multithreading support.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer для AI chat.
    Handles real-time messaging між client та AI agent.
    
    TODO: Activate після встановлення channels package.
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        Створює нову conversation або restore existing.
        """
        # Get session_id з URL
        self.session_id = self.scope['url_route']['kwargs'].get('session_id')
        self.user = self.scope.get('user')
        
        # Join room group
        self.room_group_name = f'chat_{self.session_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"WebSocket connected: {self.session_id}")
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'session_id': str(self.session_id),
            'message': 'Вітаємо в CoreSync! Як я можу вам допомогти?',
            'timestamp': datetime.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"WebSocket disconnected: {self.session_id}, code: {close_code}")
    
    async def receive(self, text_data):
        """
        Receive message від client та process через AI agent.
        """
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            
            if not message:
                return
            
            logger.info(f"Received message: {message[:50]}")
            
            # Process через AI Agent Core
            from ai_agent.agent_core import AIAgentCore
            
            agent = AIAgentCore()
            result = await agent.process_message(
                session_id=self.session_id,
                user_message=message,
                user_id=self.user.id if self.user and self.user.is_authenticated else None,
                source='web_chat'
            )
            
            # Send response назад до client
            await self.send(text_data=json.dumps({
                'type': 'agent_response',
                'message': result['response'],
                'intent': result.get('intent', {}),
                'next_action': result.get('next_action'),
                'processing_time_ms': result.get('processing_time_ms', 0),
                'timestamp': datetime.now().isoformat()
            }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Виникла помилка. Спробуйте ще раз.'
            }))
    
    async def chat_message(self, event):
        """
        Receive message від room group.
        Для multi-user support (Phase 2).
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'timestamp': event.get('timestamp')
        }))

