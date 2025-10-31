"""
API views for user management and authentication.

This module provides REST API endpoints for:
- User authentication (login, logout, token refresh)
- User registration and profile management
- User administration (admin-only)
- User preferences and settings
"""

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .models import User, UserSession, UserPreferences
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    UserAdminSerializer,
    UserSessionSerializer,
    UserPreferencesSerializer
)
from .permissions import IsAdminUser, IsOwnerOrAdmin


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that accepts email instead of username.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Track user session
            user_email = request.data.get('email')
            try:
                user = User.objects.get(email=user_email)
                ip_address = self.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                # Update last login IP
                user.update_last_login_ip(ip_address)
                
                # Create/update session record
                UserSession.objects.update_or_create(
                    user=user,
                    ip_address=ip_address,
                    defaults={
                        'user_agent': user_agent,
                        'last_activity': timezone.now(),
                        'is_active': True
                    }
                )
            except User.DoesNotExist:
                pass
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@extend_schema(
    summary="User logout",
    description="Logout user and invalidate refresh token",
    request=None,
    responses={200: {"description": "Successfully logged out"}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user and blacklist their refresh token.
    """
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Deactivate user sessions
        UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).update(is_active=False)
        
        return Response(
            {"message": "Successfully logged out"}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": "Invalid token"}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user account.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register new user",
        description="Create a new user account with email and password",
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(
            {
                "message": "User registered successfully",
                "user": UserProfileSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user profile information.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer
    
    @extend_schema(
        summary="Get user profile",
        description="Retrieve the authenticated user's profile information",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user profile",
        description="Update the authenticated user's profile information",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PasswordChangeView(generics.GenericAPIView):
    """
    Change user password.
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change the authenticated user's password",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )


class UserPreferencesView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user preferences.
    """
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        preferences, created = UserPreferences.objects.get_or_create(
            user=self.request.user
        )
        return preferences
    
    @extend_schema(
        summary="Get user preferences",
        description="Retrieve the authenticated user's preferences",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user preferences",
        description="Update the authenticated user's preferences",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['role', 'is_active', 'organization']
    search_fields = ['email', 'username', 'full_name', 'organization']
    ordering_fields = ['email', 'full_name', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    @extend_schema(
        summary="List users",
        description="List all users with admin permissions",
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, description='Search in email, username, full_name, organization'),
            OpenApiParameter('role', OpenApiTypes.STR, description='Filter by user role'),
            OpenApiParameter('is_active', OpenApiTypes.BOOL, description='Filter by active status'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get user details",
        description="Get detailed information about a specific user",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user",
        description="Update user information (admin only)",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Deactivate user",
        description="Deactivate a user account",
    )
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        
        # Deactivate all user sessions
        UserSession.objects.filter(user=user).update(is_active=False)
        
        return Response({"message": f"User {user.email} deactivated"})
    
    @extend_schema(
        summary="Activate user",
        description="Activate a user account",
    )
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({"message": f"User {user.email} activated"})
    
    @extend_schema(
        summary="Get user sessions",
        description="Get all active sessions for a user",
    )
    @action(detail=True, methods=['get'])
    def sessions(self, request, pk=None):
        user = self.get_object()
        sessions = UserSession.objects.filter(user=user, is_active=True)
        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data)


@extend_schema(
    summary="System status",
    description="Check system status and user statistics",
    responses={200: {"description": "System status information"}}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_status(request):
    """
    Get system status information.
    """
    if not request.user.is_admin:
        return Response(
            {"error": "Admin access required"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = User.objects.filter(role=User.Role.ADMIN).count()
    active_sessions = UserSession.objects.filter(is_active=True).count()
    
    return Response({
        "users": {
            "total": total_users,
            "active": active_users,
            "admins": admin_users,
        },
        "sessions": {
            "active": active_sessions,
        },
        "system": {
            "status": "operational",
            "version": "2.0.0",
        }
    })
