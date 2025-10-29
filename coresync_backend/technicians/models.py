"""
Technicians Models - Technician portal, scheduling, hours tracking.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class Technician(models.Model):
    """
    Technician profile - linked до User.
    ~20 hrs/week flexible scheduling.
    """
    SPECIALTY_CHOICES = [
        ('massage', 'Massage Therapist'),
        ('facial', 'Facial Specialist'),
        ('barber', 'Barber'),
        ('manicure', 'Manicure/Pedicure'),
        ('all', 'All Services'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='technician_profile'
    )
    
    specialties = models.JSONField(
        default=list,
        help_text="List of specialties: ['massage', 'facial', ...]"
    )
    
    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Hourly rate для payroll calculation"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Active technician (can receive bookings)"
    )
    
    # Google Sheets sync
    google_sheet_row_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Row ID в Google Sheet для sync"
    )
    
    # Metadata
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    certification_number = models.CharField(max_length=100, blank=True)
    
    hired_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
        ]
        verbose_name = "Technician"
        verbose_name_plural = "Technicians"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {', '.join(self.specialties)}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email
    
    def get_weekly_hours_total(self, week_start_date):
        """Calculate total hours для заданого тижня."""
        week_end = week_start_date + timezone.timedelta(days=7)
        
        total = self.work_logs.filter(
            date__gte=week_start_date,
            date__lt=week_end,
            approved=True
        ).aggregate(
            total=models.Sum('hours')
        )['total']
        
        return total or Decimal('0.00')


class WorkLog(models.Model):
    """
    Work hours log для technicians.
    Auto-syncs до Google Sheets для payroll.
    """
    technician = models.ForeignKey(
        Technician,
        on_delete=models.CASCADE,
        related_name='work_logs'
    )
    
    date = models.DateField(default=timezone.now)
    
    hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('24.00'))
        ],
        help_text="Hours worked (decimal format, e.g. 8.5)"
    )
    
    # Approval workflow
    approved = models.BooleanField(
        default=False,
        help_text="Manager approval required"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_worklogs'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Google Sheets sync
    synced_to_sheets = models.BooleanField(
        default=False,
        help_text="Synced до Google Sheets"
    )
    synced_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes або break details"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', 'technician']
        indexes = [
            models.Index(fields=['technician', '-date']),
            models.Index(fields=['approved', '-date']),
            models.Index(fields=['synced_to_sheets', '-date']),
        ]
        unique_together = [['technician', 'date']]  # One log per day
        verbose_name = "Work Log"
        verbose_name_plural = "Work Logs"
    
    def __str__(self):
        return f"{self.technician.full_name} - {self.date} ({self.hours}h)"
    
    def approve(self, approved_by_user):
        """Manager approval."""
        self.approved = True
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save(update_fields=['approved', 'approved_by', 'approved_at'])
    
    def mark_synced(self):
        """Mark as synced до Google Sheets."""
        self.synced_to_sheets = True
        self.synced_at = timezone.now()
        self.save(update_fields=['synced_to_sheets', 'synced_at'])


class Schedule(models.Model):
    """
    Technician availability schedule.
    Recurring weekly або one-time slots.
    """
    WEEKDAY_CHOICES = [
        (0, 'Понеділок'),
        (1, 'Вівторок'),
        (2, 'Середа'),
        (3, 'Четвер'),
        (4, 'П\'ятниця'),
        (5, 'Субота'),
        (6, 'Неділя'),
    ]
    
    technician = models.ForeignKey(
        Technician,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    # Recurring або specific date
    is_recurring = models.BooleanField(
        default=True,
        help_text="Recurring weekly або one-time"
    )
    
    weekday = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        null=True,
        blank=True,
        help_text="Weekday (0=Mon, 6=Sun) для recurring"
    )
    
    specific_date = models.DateField(
        null=True,
        blank=True,
        help_text="Specific date для one-time schedule"
    )
    
    # Time range
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Active schedule slot"
    )
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['technician', 'weekday', 'start_time']
        indexes = [
            models.Index(fields=['technician', 'is_active']),
            models.Index(fields=['weekday', 'is_active']),
            models.Index(fields=['specific_date']),
        ]
        verbose_name = "Technician Schedule"
        verbose_name_plural = "Technician Schedules"
    
    def __str__(self):
        if self.is_recurring:
            day_name = dict(self.WEEKDAY_CHOICES)[self.weekday]
            return f"{self.technician.full_name} - {day_name} {self.start_time}-{self.end_time}"
        else:
            return f"{self.technician.full_name} - {self.specific_date} {self.start_time}-{self.end_time}"
    
    def clean(self):
        """Validation."""
        from django.core.exceptions import ValidationError
        
        if self.is_recurring and self.weekday is None:
            raise ValidationError("Recurring schedule must have weekday")
        
        if not self.is_recurring and self.specific_date is None:
            raise ValidationError("Non-recurring schedule must have specific date")
        
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
