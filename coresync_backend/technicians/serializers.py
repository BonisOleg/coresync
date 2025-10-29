"""
Technicians Serializers - API serialization.
"""
from rest_framework import serializers
from .models import Technician, WorkLog, Schedule


class TechnicianSerializer(serializers.ModelSerializer):
    """Technician profile serializer."""
    
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    weekly_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Technician
        fields = [
            'id',
            'full_name',
            'email',
            'specialties',
            'hourly_rate',
            'is_active',
            'bio',
            'phone',
            'hired_date',
            'weekly_hours'
        ]
        read_only_fields = ['id', 'full_name', 'email']
    
    def get_weekly_hours(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=today.weekday())
        return float(obj.get_weekly_hours_total(week_start))


class WorkLogSerializer(serializers.ModelSerializer):
    """Work log serializer."""
    
    technician_name = serializers.CharField(source='technician.full_name', read_only=True)
    
    class Meta:
        model = WorkLog
        fields = [
            'id',
            'technician',
            'technician_name',
            'date',
            'hours',
            'approved',
            'approved_by',
            'approved_at',
            'synced_to_sheets',
            'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'approved_by', 'approved_at', 'synced_to_sheets', 'created_at']


class ScheduleSerializer(serializers.ModelSerializer):
    """Schedule serializer."""
    
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id',
            'technician',
            'is_recurring',
            'weekday',
            'weekday_display',
            'specific_date',
            'start_time',
            'end_time',
            'is_active',
            'notes'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate schedule data."""
        if data.get('is_recurring') and not data.get('weekday'):
            raise serializers.ValidationError("Recurring schedule must have weekday")
        
        if not data.get('is_recurring') and not data.get('specific_date'):
            raise serializers.ValidationError("Non-recurring schedule must have specific date")
        
        if data.get('start_time') >= data.get('end_time'):
            raise serializers.ValidationError("End time must be after start time")
        
        return data

