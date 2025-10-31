"""
URL patterns for the mapping app.

This module defines all the API endpoints for field mapping functionality,
including source table discovery, target schema management, and mapping operations.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SourceTableViewSet,
    TargetSchemaViewSet,
    FieldMappingViewSet,
    AIMappingViewSet,
    MappingTemplateViewSet,
    MappingSessionViewSet,
    mapping_stats,
)

# Create a router for viewsets
router = DefaultRouter()
router.register(r'source-tables', SourceTableViewSet, basename='source-tables')
router.register(r'target-schemas', TargetSchemaViewSet, basename='target-schemas')
router.register(r'field-mappings', FieldMappingViewSet, basename='field-mappings')
router.register(r'ai-suggestions', AIMappingViewSet, basename='ai-suggestions')
router.register(r'templates', MappingTemplateViewSet, basename='templates')
router.register(r'sessions', MappingSessionViewSet, basename='sessions')

app_name = 'mapping'

urlpatterns = [
    # Statistics endpoint
    path('stats/', mapping_stats, name='mapping_stats'),
    
    # Include router URLs
    path('', include(router.urls)),
]
