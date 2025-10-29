"""
AI Agent Models - Conversation tracking and analytics.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class Conversation(models.Model):
    """
    Tracks AI agent conversation sessions (chat + phone).
    Links user requests to booking outcomes.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
        ('error', 'Error'),
    ]
    
    SOURCE_CHOICES = [
        ('web_chat', 'Website Chat'),
        ('atlas_phone', 'Atlas Phone Call'),
        ('atlas_sms', 'Atlas SMS'),
    ]
    
    session_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True,
        db_index=True
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ai_conversations',
        help_text="Authenticated user or null for anonymous"
    )
    source = models.CharField(
        max_length=20, 
        choices=SOURCE_CHOICES,
        default='web_chat'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Context data (stored as JSON)
    context_data = models.JSONField(
        default=dict,
        help_text="Conversation state, user preferences, detected intents"
    )
    
    # Booking outcome
    booking = models.ForeignKey(
        'services.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_conversations',
        help_text="Booking created from this conversation"
    )
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['-started_at']),
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['user', '-started_at']),
        ]
        verbose_name = "AI Conversation"
        verbose_name_plural = "AI Conversations"
    
    def __str__(self):
        user_str = self.user.email if self.user else "Anonymous"
        return f"{self.session_id} - {user_str} ({self.get_source_display()})"
    
    @property
    def duration_minutes(self):
        """Calculate conversation duration in minutes."""
        if self.ended_at:
            delta = self.ended_at - self.started_at
            return round(delta.total_seconds() / 60, 2)
        return None
    
    def mark_completed(self):
        """Mark conversation as completed."""
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at'])
    
    def mark_abandoned(self):
        """Mark conversation as abandoned."""
        self.status = 'abandoned'
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at'])


class AgentAction(models.Model):
    """
    Individual actions/messages within a conversation.
    Tracks all AI agent interactions for debugging and analytics.
    """
    ACTION_TYPES = [
        ('user_message', 'User Message'),
        ('agent_response', 'Agent Response'),
        ('intent_detected', 'Intent Detected'),
        ('api_call', 'API Call'),
        ('booking_check', 'Availability Check'),
        ('payment_request', 'Payment Request'),
        ('error', 'Error'),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='actions'
    )
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    
    # Content
    query = models.TextField(
        blank=True,
        help_text="User input or agent query"
    )
    response = models.TextField(
        blank=True,
        help_text="Agent response or API result"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        help_text="Additional data (intent confidence, API params, etc.)"
    )
    
    # Performance tracking
    processing_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time taken to process this action (milliseconds)"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
        ]
        verbose_name = "Agent Action"
        verbose_name_plural = "Agent Actions"
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.timestamp}"


class AtlasLog(models.Model):
    """
    Raw logs from Atlas AI webhooks (phone/SMS).
    Stores complete webhook payloads for debugging.
    """
    # Webhook data
    webhook_data = models.JSONField(help_text="Complete Atlas webhook payload")
    
    # Processing status
    processed = models.BooleanField(
        default=False,
        help_text="Has this webhook been processed?"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error details if processing failed"
    )
    
    # Link to conversation
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atlas_logs'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['processed', '-created_at']),
        ]
        verbose_name = "Atlas Webhook Log"
        verbose_name_plural = "Atlas Webhook Logs"
    
    def __str__(self):
        status = "✅ Processed" if self.processed else "⏳ Pending"
        return f"Atlas Log {self.id} - {status}"
    
    def mark_processed(self):
        """Mark log as successfully processed."""
        self.processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['processed', 'processed_at'])
