"""
User models for the Source-to-Target Mapping Platform.

This module defines custom user models with role-based permissions
for managing access to mapping functionality and administration.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model with additional fields for the mapping platform.
    
    Extends Django's AbstractUser to include role management and
    platform-specific user information.
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        USER = 'user', 'User'
        VIEWER = 'viewer', 'Viewer'
    
    # Core user information
    email = models.EmailField('email address', unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        help_text='User role determining access permissions'
    )
    
    # Additional user metadata
    full_name = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Access control
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    password_changed_at = models.DateTimeField(default=timezone.now)
    
    # Databricks access (optional)
    databricks_user_id = models.CharField(max_length=255, blank=True, null=True)
    databricks_workspace_url = models.URLField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['email']
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Check if user has admin privileges."""
        return self.role == self.Role.ADMIN
    
    @property
    def is_platform_user(self):
        """Check if user has platform access (not just viewer)."""
        return self.role in [self.Role.ADMIN, self.Role.USER]
    
    @property
    def display_name(self):
        """Get the best display name for the user."""
        if self.full_name:
            return self.full_name
        return self.username or self.email.split('@')[0]
    
    def can_access_mapping(self):
        """Check if user can access mapping functionality."""
        return self.is_active and self.is_platform_user
    
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.is_active and self.is_admin
    
    def can_manage_configuration(self):
        """Check if user can manage system configuration."""
        return self.is_active and self.is_admin
    
    def update_last_login_ip(self, ip_address):
        """Update the user's last login IP address."""
        self.last_login_ip = ip_address
        self.save(update_fields=['last_login_ip'])


class UserSession(models.Model):
    """
    Track active user sessions for security and monitoring.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"


class UserPreferences(models.Model):
    """
    Store user-specific preferences and settings.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # UI Preferences
    theme = models.CharField(
        max_length=20,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto'
    )
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    mapping_completion_notifications = models.BooleanField(default=True)
    ai_suggestion_notifications = models.BooleanField(default=False)
    
    # Default Settings
    default_page_size = models.IntegerField(default=50)
    auto_save_mappings = models.BooleanField(default=True)
    show_advanced_options = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.email}"