"""
URL configuration for configuration management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ConfigurationViewSet, ConfigurationTemplateViewSet, ConfigurationHistoryViewSet

app_name = 'configuration'

# Create a router for viewsets
router = DefaultRouter()
router.register(r'settings', ConfigurationViewSet, basename='configuration')
router.register(r'templates', ConfigurationTemplateViewSet, basename='configuration-template')
router.register(r'history', ConfigurationHistoryViewSet, basename='configuration-history')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
