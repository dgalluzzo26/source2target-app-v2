"""
Serializers for the accounts app.

This module defines DRF serializers for user authentication,
registration, profile management, and user administration.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User, UserSession, UserPreferences


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes additional user data.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field and use email instead
        self.fields.pop('username', None)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Authenticate using email instead of username
            try:
                user = User.objects.get(email=email)
                attrs['username'] = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid email or password.')

        data = super().validate(attrs)
        
        # Add custom claims to the token
        refresh = self.get_token(self.user)
        refresh['email'] = self.user.email
        refresh['role'] = self.user.role
        refresh['full_name'] = self.user.full_name or self.user.display_name
        
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = UserProfileSerializer(self.user).data
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'password', 'password_confirm',
            'full_name', 'organization', 'department', 'phone_number'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user preferences
        UserPreferences.objects.create(user=user)
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    """
    display_name = serializers.ReadOnlyField()
    is_admin = serializers.ReadOnlyField()
    is_platform_user = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'full_name', 'display_name',
            'organization', 'department', 'phone_number', 'role',
            'is_admin', 'is_platform_user', 'is_active',
            'last_login', 'date_joined', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'email', 'username', 'role', 'is_active',
            'last_login', 'date_joined', 'created_at', 'updated_at'
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    """
    
    class Meta:
        model = User
        fields = (
            'full_name', 'organization', 'department', 'phone_number'
        )
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.password_changed_at = timezone.now()
        user.save()
        return user


class UserAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for user administration (admin-only).
    """
    display_name = serializers.ReadOnlyField()
    session_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'full_name', 'display_name',
            'organization', 'department', 'phone_number', 'role',
            'is_active', 'is_staff', 'is_superuser',
            'last_login', 'last_login_ip', 'date_joined',
            'created_at', 'updated_at', 'session_count'
        )
        read_only_fields = ('id', 'email', 'username', 'date_joined', 'created_at')
    
    def get_session_count(self, obj):
        return obj.sessions.filter(is_active=True).count()


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for user session information.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserSession
        fields = (
            'id', 'user_email', 'ip_address', 'user_agent',
            'created_at', 'last_activity', 'is_active'
        )
        read_only_fields = ('id', 'user_email', 'created_at')


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializer for user preferences.
    """
    
    class Meta:
        model = UserPreferences
        fields = (
            'theme', 'language', 'timezone',
            'email_notifications', 'mapping_completion_notifications',
            'ai_suggestion_notifications', 'default_page_size',
            'auto_save_mappings', 'show_advanced_options'
        )
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
