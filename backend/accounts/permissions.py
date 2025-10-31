"""
Custom permissions for the accounts app.

This module defines role-based permissions for the Source-to-Target
Mapping Platform, ensuring proper access control for different user roles.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission that only allows admin users to access the view.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that allows users to access their own resources or admins to access all.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is an admin
        if request.user.is_admin:
            return True
        
        # Check if the object has a user attribute and it matches the requesting user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If the object is the user itself
        return obj == request.user


class IsPlatformUser(permissions.BasePermission):
    """
    Permission that only allows platform users (not viewers) to access the view.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_platform_user
        )


class CanAccessMapping(permissions.BasePermission):
    """
    Permission that checks if user can access mapping functionality.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_access_mapping()
        )


class CanManageConfiguration(permissions.BasePermission):
    """
    Permission that checks if user can manage system configuration.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.can_manage_configuration()
        )


class ReadOnlyOrAdmin(permissions.BasePermission):
    """
    Permission that allows read-only access to all authenticated users,
    but write access only to admins.
    """
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admins
        return request.user.is_admin
