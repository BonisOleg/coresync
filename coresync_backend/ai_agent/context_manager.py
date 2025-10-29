"""
Context Manager - Redis-based conversation context storage.
Manages session state, user preferences, conversation flow.
"""
import json
import logging
from typing import Dict, Any, Optional
from datetime import timedelta

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages conversation context в Redis.
    TTL: 30 minutes (auto-cleanup inactive sessions).
    """
    
    def __init__(self, ttl_minutes: int = 30):
        self.ttl = timedelta(minutes=ttl_minutes)
        self.redis_client = self._get_redis_client()
    
    def _get_redis_client(self):
        """
        Get Redis client connection.
        
        TODO: Activate після встановлення redis package.
        """
        try:
            import redis
            from django.conf import settings
            
            redis_url = settings.CELERY_BROKER_URL
            return redis.from_url(redis_url, decode_responses=True)
        
        except ImportError:
            logger.warning("Redis not installed, using in-memory fallback")
            return None
        
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            return None
    
    def _get_key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"ai:context:{session_id}"
    
    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve conversation context from Redis.
        
        Args:
            session_id: UUID сесії
        
        Returns:
            Dict з context data або empty dict
        """
        try:
            if not self.redis_client:
                return self._get_default_context()
            
            from asgiref.sync import sync_to_async
            
            # Redis get operation
            get_operation = sync_to_async(
                self.redis_client.get,
                thread_sensitive=False
            )
            
            key = self._get_key(session_id)
            data = await get_operation(key)
            
            if data:
                return json.loads(data)
            else:
                return self._get_default_context()
        
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return self._get_default_context()
    
    async def set_context(self, session_id: str, context: Dict[str, Any]) -> bool:
        """
        Save conversation context to Redis з TTL.
        
        Args:
            session_id: UUID сесії
            context: Context data
        
        Returns:
            True if successful
        """
        try:
            if not self.redis_client:
                logger.warning("Redis not available, context not saved")
                return False
            
            from asgiref.sync import sync_to_async
            
            # Redis setex operation (set with expiry)
            setex_operation = sync_to_async(
                self.redis_client.setex,
                thread_sensitive=False
            )
            
            key = self._get_key(session_id)
            data = json.dumps(context)
            ttl_seconds = int(self.ttl.total_seconds())
            
            await setex_operation(key, ttl_seconds, data)
            return True
        
        except Exception as e:
            logger.error(f"Error setting context: {str(e)}")
            return False
    
    async def delete_context(self, session_id: str) -> bool:
        """
        Delete conversation context (cleanup).
        
        Args:
            session_id: UUID сесії
        
        Returns:
            True if successful
        """
        try:
            if not self.redis_client:
                return False
            
            from asgiref.sync import sync_to_async
            
            delete_operation = sync_to_async(
                self.redis_client.delete,
                thread_sensitive=False
            )
            
            key = self._get_key(session_id)
            await delete_operation(key)
            return True
        
        except Exception as e:
            logger.error(f"Error deleting context: {str(e)}")
            return False
    
    def _get_default_context(self) -> Dict[str, Any]:
        """Default empty context."""
        return {
            'message_count': 0,
            'detected_intents': [],
            'user_preferences': {},
            'booking_data': {},
            'last_intent': None,
            'created_at': None,
            'updated_at': None
        }
    
    async def extend_ttl(self, session_id: str) -> bool:
        """
        Extend TTL на активні розмови.
        
        Args:
            session_id: UUID сесії
        
        Returns:
            True if successful
        """
        try:
            if not self.redis_client:
                return False
            
            from asgiref.sync import sync_to_async
            
            expire_operation = sync_to_async(
                self.redis_client.expire,
                thread_sensitive=False
            )
            
            key = self._get_key(session_id)
            ttl_seconds = int(self.ttl.total_seconds())
            
            await expire_operation(key, ttl_seconds)
            return True
        
        except Exception as e:
            logger.error(f"Error extending TTL: {str(e)}")
            return False

