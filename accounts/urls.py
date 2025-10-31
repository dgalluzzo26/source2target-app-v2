"""
URL patterns for the accounts app.

This module defines all the API endpoints for user authentication,
registration, profile management, and administration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    logout_view,
    UserRegistrationView,
    UserProfileView,
    PasswordChangeView,
    UserPreferencesView,
    UserAdminViewSet,
    system_status,
)

# Create a router for viewsets
router = DefaultRouter()
router.register(r'admin/users', UserAdminViewSet, basename='admin-users')

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('preferences/', UserPreferencesView.as_view(), name='preferences'),
    
    # Admin endpoints
    path('system/status/', system_status, name='system_status'),
    
    # Include router URLs
    path('', include(router.urls)),
]
