"""
AI Agent App Configuration.
"""
from django.apps import AppConfig


class AiAgentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_agent'
    verbose_name = 'AI Agent & Conversations'
    
    def ready(self):
        """Import signals when app is ready."""
        try:
            import ai_agent.signals  # noqa
        except ImportError:
            pass
