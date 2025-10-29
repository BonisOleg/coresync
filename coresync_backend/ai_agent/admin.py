"""
AI Agent Django Admin configuration.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, AgentAction, AtlasLog


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = [
        'session_id_short',
        'user_email',
        'source',
        'status_badge',
        'booking_link',
        'started_at',
        'duration_display',
        'actions_count'
    ]
    list_filter = ['status', 'source', 'started_at']
    search_fields = ['session_id', 'user__email', 'ip_address']
    readonly_fields = [
        'session_id', 
        'started_at', 
        'ended_at', 
        'last_activity',
        'duration_display'
    ]
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'user', 'source', 'status')
        }),
        ('Booking Outcome', {
            'fields': ('booking',)
        }),
        ('Context Data', {
            'fields': ('context_data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('started_at', 'ended_at', 'last_activity', 'duration_display')
        }),
    )
    
    def session_id_short(self, obj):
        return str(obj.session_id)[:8]
    session_id_short.short_description = 'Session'
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '—'
    user_email.short_description = 'User'
    
    def status_badge(self, obj):
        colors = {
            'active': '#28a745',
            'completed': '#007bff',
            'abandoned': '#ffc107',
            'error': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 3px; '
            'background: {}; color: white; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def booking_link(self, obj):
        if obj.booking:
            return format_html(
                '<a href="/admin/services/booking/{}/change/">Booking #{}</a>',
                obj.booking.id, obj.booking.id
            )
        return '—'
    booking_link.short_description = 'Booking'
    
    def duration_display(self, obj):
        duration = obj.duration_minutes
        if duration:
            return f"{duration} min"
        return '—'
    duration_display.short_description = 'Duration'
    
    def actions_count(self, obj):
        return obj.actions.count()
    actions_count.short_description = 'Actions'


@admin.register(AgentAction)
class AgentActionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'conversation_session',
        'action_type_badge',
        'query_preview',
        'processing_time',
        'timestamp'
    ]
    list_filter = ['action_type', 'timestamp']
    search_fields = ['conversation__session_id', 'query', 'response']
    readonly_fields = ['timestamp', 'processing_time_ms']
    
    fieldsets = (
        ('Conversation', {
            'fields': ('conversation', 'action_type')
        }),
        ('Content', {
            'fields': ('query', 'response')
        }),
        ('Metadata', {
            'fields': ('metadata', 'processing_time_ms'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )
    
    def conversation_session(self, obj):
        return str(obj.conversation.session_id)[:8]
    conversation_session.short_description = 'Session'
    
    def action_type_badge(self, obj):
        colors = {
            'user_message': '#17a2b8',
            'agent_response': '#28a745',
            'intent_detected': '#ffc107',
            'api_call': '#6f42c1',
            'booking_check': '#fd7e14',
            'payment_request': '#e83e8c',
            'error': '#dc3545',
        }
        color = colors.get(obj.action_type, '#6c757d')
        return format_html(
            '<span style="padding: 2px 6px; border-radius: 3px; '
            'background: {}; color: white; font-size: 11px;">{}</span>',
            color, obj.get_action_type_display()
        )
    action_type_badge.short_description = 'Type'
    
    def query_preview(self, obj):
        if obj.query:
            preview = obj.query[:50]
            return f"{preview}..." if len(obj.query) > 50 else preview
        return '—'
    query_preview.short_description = 'Query Preview'
    
    def processing_time(self, obj):
        if obj.processing_time_ms:
            return f"{obj.processing_time_ms}ms"
        return '—'
    processing_time.short_description = 'Time'


@admin.register(AtlasLog)
class AtlasLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'processed_badge',
        'conversation_link',
        'created_at',
        'error_preview'
    ]
    list_filter = ['processed', 'created_at']
    search_fields = ['webhook_data', 'error_message']
    readonly_fields = ['created_at', 'processed_at', 'webhook_data']
    
    fieldsets = (
        ('Processing Status', {
            'fields': ('processed', 'processed_at', 'error_message')
        }),
        ('Webhook Data', {
            'fields': ('webhook_data',),
            'classes': ('collapse',)
        }),
        ('Link', {
            'fields': ('conversation',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def processed_badge(self, obj):
        if obj.processed:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Processed</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
        )
    processed_badge.short_description = 'Status'
    
    def conversation_link(self, obj):
        if obj.conversation:
            return format_html(
                '<a href="/admin/ai_agent/conversation/{}/change/">{}</a>',
                obj.conversation.id, 
                str(obj.conversation.session_id)[:8]
            )
        return '—'
    conversation_link.short_description = 'Conversation'
    
    def error_preview(self, obj):
        if obj.error_message:
            preview = obj.error_message[:40]
            return format_html(
                '<span style="color: red;">{}</span>',
                f"{preview}..." if len(obj.error_message) > 40 else preview
            )
        return '—'
    error_preview.short_description = 'Error'
