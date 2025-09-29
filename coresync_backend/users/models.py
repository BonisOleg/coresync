"""
User models for the CoreSync application.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """
    Custom user model for CoreSync members and customers.
    """
    MEMBERSHIP_CHOICES = [
        ('none', 'Non-Member'),
        ('basic', 'Basic Member'),
        ('premium', 'Premium Member'),
        ('vip', 'VIP Member'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    membership_status = models.CharField(
        max_length=10,
        choices=MEMBERSHIP_CHOICES,
        default='none'
    )
    membership_plan = models.ForeignKey(
        'memberships.MembershipPlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    
    # Biometric data (encrypted)
    face_recognition_data = models.TextField(blank=True, null=True)
    biometric_enabled = models.BooleanField(default=False)
    
    # Additional profile information
    date_of_birth = models.DateField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_member(self):
        return self.membership_status != 'none'

    def get_member_discount(self):
        """Get the discount percentage for this user based on membership."""
        if self.membership_plan:
            return self.membership_plan.discount_percentage
        return 0


class UserPreference(TimeStampedModel):
    """
    User preferences for spa environment control.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    
    # Scene preferences
    default_scene_name = models.CharField(max_length=100, blank=True)
    scene_config = models.JSONField(default=dict, blank=True)
    
    # Scent preferences
    favorite_scents = models.JSONField(default=list, blank=True)
    scent_intensity = models.IntegerField(
        default=3,
        choices=[(i, str(i)) for i in range(1, 6)]  # 1-5 scale
    )
    
    # Lighting preferences
    lighting_type = models.CharField(
        max_length=50,
        choices=[
            ('warm', 'Warm'),
            ('cool', 'Cool'),
            ('natural', 'Natural'),
            ('colored', 'Colored'),
        ],
        default='warm'
    )
    lighting_intensity = models.IntegerField(
        default=70,
        help_text="Lighting intensity from 0-100%"
    )
    
    # Temperature preferences
    preferred_temperature = models.FloatField(
        default=72.0,
        help_text="Preferred temperature in Fahrenheit"
    )
    
    # Music preferences
    music_genre = models.CharField(max_length=50, blank=True)
    music_volume = models.IntegerField(
        default=30,
        help_text="Music volume from 0-100%"
    )

    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"Preferences for {self.user.full_name}"
