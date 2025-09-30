"""
DRF Serializers for Users app.
Clean, safe serializers without conflicts.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserPreference


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user spa preferences"""
    
    class Meta:
        model = UserPreference
        fields = [
            'id', 'default_scene_name', 'scene_config',
            'favorite_scents', 'scent_intensity',
            'lighting_type', 'lighting_intensity',
            'preferred_temperature', 'music_genre', 'music_volume',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information"""
    
    preferences = UserPreferenceSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    is_member = serializers.ReadOnlyField()
    member_discount = serializers.SerializerMethodField()
    
    def get_member_discount(self, obj):
        """Get user's membership discount percentage"""
        return obj.get_member_discount()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'membership_status', 'is_member', 'member_discount',
            'date_of_birth', 'emergency_contact', 'emergency_phone',
            'email_notifications', 'sms_notifications',
            'biometric_enabled', 'preferences', 'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'membership_status', 'is_member', 
            'member_discount', 'date_joined', 'last_login'
        ]
        extra_kwargs = {
            'email': {'required': False},  # Don't require email in updates
        }
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value:
            # Basic phone number validation
            import re
            phone_pattern = r'^\+?1?\d{9,15}$'
            if not re.match(phone_pattern, value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
                raise serializers.ValidationError("Invalid phone number format.")
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone',
            'date_of_birth', 'emergency_contact', 'emergency_phone',
            'email_notifications', 'sms_notifications'
        ]
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value:
            import re
            phone_pattern = r'^\+?1?\d{9,15}$'
            clean_phone = value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not re.match(phone_pattern, clean_phone):
                raise serializers.ValidationError("Invalid phone number format.")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs
    
    def validate_email(self, value):
        """Check if email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Check if username is unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create default preferences for new user
        UserPreference.objects.create(user=user)
        
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New password fields didn't match.")
        return attrs
    
    def save(self):
        """Change user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class BiometricRegistrationSerializer(serializers.Serializer):
    """Serializer for biometric data registration"""
    
    face_data = serializers.CharField(help_text="Base64 encoded face data")
    biometric_type = serializers.ChoiceField(
        choices=[('face_recognition', 'Face Recognition')],
        default='face_recognition'
    )
    
    def validate_face_data(self, value):
        """Basic validation for face data"""
        if not value or len(value) < 100:  # Basic check
            raise serializers.ValidationError("Invalid face data provided.")
        
        # Here you would typically validate the base64 format
        import base64
        try:
            base64.b64decode(value)
        except Exception:
            raise serializers.ValidationError("Face data must be valid base64.")
        
        return value
    
    def save(self):
        """Save biometric data for user"""
        user = self.context['request'].user
        
        # In a real implementation, you would:
        # 1. Process the face data with face recognition service
        # 2. Store encrypted biometric template (not raw image)
        # 3. Enable biometric authentication
        
        # For now, we'll just mark biometric as enabled
        user.biometric_enabled = True
        user.face_recognition_data = "encrypted_template_placeholder"  # Would be actual encrypted data
        user.save()
        
        return user


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    
    total_services = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)
    favorite_service = serializers.CharField(allow_null=True)
    last_visit = serializers.DateTimeField(allow_null=True)
    services_this_month = serializers.IntegerField()
    membership_level = serializers.CharField()
    member_since = serializers.DateTimeField(allow_null=True)
    loyalty_points = serializers.IntegerField(default=0)  # Future feature




