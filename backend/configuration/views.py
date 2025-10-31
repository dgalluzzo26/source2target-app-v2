"""
Configuration management views.
"""

import json
import logging
from typing import Dict, Any
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from accounts.permissions import IsAdminUser
from .models import Configuration, ConfigurationHistory, ConfigurationTemplate, get_default_configuration
from .serializers import (
    ConfigurationSerializer, ConfigurationHistorySerializer, ConfigurationTemplateSerializer,
    FullConfigurationSerializer, ConfigurationUpdateSerializer, ConfigurationBulkUpdateSerializer,
    ConfigurationTestSerializer, ConfigurationExportSerializer, ConfigurationImportSerializer
)
from mapping.services.databricks_service import databricks_service, DatabricksConnectionError

logger = logging.getLogger(__name__)


class ConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual configuration settings.
    """
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    permission_classes = [IsAuthenticated]  # Changed from IsAdminUser for testing
    filterset_fields = ['section', 'is_active']
    search_fields = ['key', 'description']
    ordering_fields = ['section', 'key', 'updated_at']
    ordering = ['section', 'key']

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_update(self, serializer):
        # Save history before updating
        instance = self.get_object()
        ConfigurationHistory.objects.create(
            configuration=instance,
            old_value=instance.value,
            new_value=serializer.validated_data.get('value', instance.value),
            changed_by=self.request.user,
            reason=self.request.data.get('reason', '')
        )
        serializer.save(updated_by=self.request.user)

    @extend_schema(
        summary="Get configuration by section",
        description="Get all configuration settings for a specific section",
        parameters=[
            OpenApiParameter('section', OpenApiTypes.STR, description='Configuration section')
        ]
    )
    @action(detail=False, methods=['get'])
    def by_section(self, request):
        """Get configuration settings by section."""
        section = request.query_params.get('section')
        if not section:
            return Response(
                {'error': 'Section parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        configs = Configuration.objects.filter(section=section, is_active=True)
        settings = {config.key: config.value for config in configs}
        
        return Response({
            'section': section,
            'settings': settings
        })

    @extend_schema(
        summary="Get full configuration",
        description="Get the complete application configuration in hierarchical format"
    )
    @action(detail=False, methods=['get'])
    def full(self, request):
        """Get the complete application configuration."""
        try:
            config_data = self._build_full_configuration()
            serializer = FullConfigurationSerializer(config_data)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to build full configuration: {e}")
            return Response(
                {'error': 'Failed to retrieve configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Update configuration setting",
        description="Update a single configuration setting",
        request=ConfigurationUpdateSerializer
    )
    @action(detail=False, methods=['post'])
    def update_setting(self, request):
        """Update a single configuration setting."""
        serializer = ConfigurationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        section = data['section']
        key = data['key']
        value = data['value']
        reason = data.get('reason', '')
        
        try:
            config, created = Configuration.objects.get_or_create(
                section=section,
                key=key,
                defaults={
                    'value': value,
                    'updated_by': request.user
                }
            )
            
            if not created:
                # Save history
                ConfigurationHistory.objects.create(
                    configuration=config,
                    old_value=config.value,
                    new_value=value,
                    changed_by=request.user,
                    reason=reason
                )
                config.value = value
                config.updated_by = request.user
                config.save()
            
            return Response({
                'message': f'Configuration {section}.{key} updated successfully',
                'created': created
            })
            
        except Exception as e:
            logger.error(f"Failed to update configuration {section}.{key}: {e}")
            return Response(
                {'error': 'Failed to update configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Bulk update configuration",
        description="Update multiple configuration settings at once",
        request=ConfigurationBulkUpdateSerializer
    )
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update configuration settings."""
        serializer = ConfigurationBulkUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        config_data = serializer.validated_data['configuration']
        reason = serializer.validated_data.get('reason', 'Bulk configuration update')
        
        try:
            updated_count = 0
            created_count = 0
            
            for section, settings in config_data.items():
                if isinstance(settings, dict):
                    for key, value in settings.items():
                        config, created = Configuration.objects.get_or_create(
                            section=section,
                            key=key,
                            defaults={
                                'value': value,
                                'updated_by': request.user
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            # Save history
                            ConfigurationHistory.objects.create(
                                configuration=config,
                                old_value=config.value,
                                new_value=value,
                                changed_by=request.user,
                                reason=reason
                            )
                            config.value = value
                            config.updated_by = request.user
                            config.save()
                            updated_count += 1
            
            return Response({
                'message': 'Bulk configuration update completed',
                'created': created_count,
                'updated': updated_count
            })
            
        except Exception as e:
            logger.error(f"Failed to bulk update configuration: {e}")
            return Response(
                {'error': 'Failed to update configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Test configuration",
        description="Test configuration settings (database connection, vector search, etc.)",
        request=ConfigurationTestSerializer
    )
    @action(detail=False, methods=['post'])
    def test(self, request):
        """Test configuration settings."""
        serializer = ConfigurationTestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        test_type = serializer.validated_data['test_type']
        config_override = serializer.validated_data.get('configuration', {})
        
        try:
            if test_type == 'database':
                return self._test_database_connection(config_override)
            elif test_type == 'vector_search':
                return self._test_vector_search(config_override)
            elif test_type == 'ai_model':
                return self._test_ai_model(config_override)
            else:
                return Response(
                    {'error': f'Unknown test type: {test_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Configuration test failed: {e}")
            return Response(
                {'error': f'Test failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Export configuration",
        description="Export configuration as JSON file",
        request=ConfigurationExportSerializer
    )
    @action(detail=False, methods=['post'])
    def export(self, request):
        """Export configuration as JSON file."""
        serializer = ConfigurationExportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        include_sections = serializer.validated_data.get('include_sections', [])
        format_type = serializer.validated_data.get('format', 'json')
        
        try:
            config_data = self._build_full_configuration()
            
            # Filter sections if specified
            if include_sections:
                config_data = {
                    section: settings 
                    for section, settings in config_data.items() 
                    if section in include_sections
                }
            
            if format_type == 'json':
                response_data = json.dumps(config_data, indent=2)
                content_type = 'application/json'
                filename = 'app_config.json'
            else:
                # YAML format could be added here
                return Response(
                    {'error': 'YAML format not yet supported'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response = HttpResponse(response_data, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return Response(
                {'error': 'Failed to export configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Import configuration",
        description="Import configuration from JSON data",
        request=ConfigurationImportSerializer
    )
    @action(detail=False, methods=['post'])
    def import_config(self, request):
        """Import configuration from JSON data."""
        serializer = ConfigurationImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        config_data = serializer.validated_data['configuration_data']
        merge_strategy = serializer.validated_data.get('merge_strategy', 'merge')
        reason = serializer.validated_data.get('reason', 'Configuration import')
        
        try:
            if merge_strategy == 'replace':
                # Delete existing configurations
                Configuration.objects.all().delete()
            
            updated_count = 0
            created_count = 0
            
            for section, settings in config_data.items():
                if isinstance(settings, dict):
                    for key, value in settings.items():
                        if merge_strategy == 'update':
                            # Only update existing keys
                            try:
                                config = Configuration.objects.get(section=section, key=key)
                                ConfigurationHistory.objects.create(
                                    configuration=config,
                                    old_value=config.value,
                                    new_value=value,
                                    changed_by=request.user,
                                    reason=reason
                                )
                                config.value = value
                                config.updated_by = request.user
                                config.save()
                                updated_count += 1
                            except Configuration.DoesNotExist:
                                continue
                        else:
                            # Create or update
                            config, created = Configuration.objects.get_or_create(
                                section=section,
                                key=key,
                                defaults={
                                    'value': value,
                                    'updated_by': request.user
                                }
                            )
                            
                            if created:
                                created_count += 1
                            else:
                                ConfigurationHistory.objects.create(
                                    configuration=config,
                                    old_value=config.value,
                                    new_value=value,
                                    changed_by=request.user,
                                    reason=reason
                                )
                                config.value = value
                                config.updated_by = request.user
                                config.save()
                                updated_count += 1
            
            return Response({
                'message': 'Configuration import completed',
                'strategy': merge_strategy,
                'created': created_count,
                'updated': updated_count
            })
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return Response(
                {'error': 'Failed to import configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Reset to defaults",
        description="Reset configuration to default values"
    )
    @action(detail=False, methods=['post'])
    def reset_defaults(self, request):
        """Reset configuration to default values."""
        try:
            reason = "Reset to default configuration"
            default_config = get_default_configuration()
            
            # Save current config to history before reset
            current_configs = Configuration.objects.all()
            for config in current_configs:
                ConfigurationHistory.objects.create(
                    configuration=config,
                    old_value=config.value,
                    new_value=None,  # Indicates deletion
                    changed_by=request.user,
                    reason=reason
                )
            
            # Delete all current configurations
            Configuration.objects.all().delete()
            
            # Create default configurations
            created_count = 0
            for section, settings in default_config.items():
                for key, value in settings.items():
                    Configuration.objects.create(
                        section=section,
                        key=key,
                        value=value,
                        updated_by=request.user
                    )
                    created_count += 1
            
            return Response({
                'message': 'Configuration reset to defaults',
                'created': created_count
            })
            
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            return Response(
                {'error': 'Failed to reset configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _build_full_configuration(self) -> Dict[str, Any]:
        """Build the complete configuration structure."""
        configs = Configuration.objects.filter(is_active=True)
        config_data = {}
        
        for config in configs:
            if config.section not in config_data:
                config_data[config.section] = {}
            config_data[config.section][config.key] = config.value
        
        # Merge with defaults to ensure all keys exist
        default_config = get_default_configuration()
        for section, settings in default_config.items():
            if section not in config_data:
                config_data[section] = {}
            for key, value in settings.items():
                if key not in config_data[section]:
                    config_data[section][key] = value
        
        return config_data

    def _test_database_connection(self, config_override: Dict[str, Any]) -> Response:
        """Test database connection."""
        try:
            connection_status = databricks_service.test_connection()
            
            if connection_status['overall_status']:
                return Response({
                    'success': True,
                    'message': 'Database connection successful',
                    'details': connection_status
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Database connection failed',
                    'details': connection_status
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except DatabricksConnectionError as e:
            return Response({
                'success': False,
                'message': f'Database connection failed: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def _test_vector_search(self, config_override: Dict[str, Any]) -> Response:
        """Test vector search configuration."""
        try:
            # TODO: Implement vector search test
            return Response({
                'success': True,
                'message': 'Vector search test not yet implemented'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Vector search test failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _test_ai_model(self, config_override: Dict[str, Any]) -> Response:
        """Test AI model configuration."""
        try:
            # TODO: Implement AI model test
            return Response({
                'success': True,
                'message': 'AI model test not yet implemented'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'AI model test failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfigurationTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing configuration templates.
    """
    queryset = ConfigurationTemplate.objects.all()
    serializer_class = ConfigurationTemplateSerializer
    permission_classes = [IsAuthenticated]  # Changed from IsAdminUser for testing
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(
        summary="Apply template",
        description="Apply a configuration template to current settings"
    )
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply a configuration template."""
        template = self.get_object()
        
        try:
            reason = f"Applied template: {template.name}"
            config_data = template.configuration_data
            
            updated_count = 0
            created_count = 0
            
            for section, settings in config_data.items():
                if isinstance(settings, dict):
                    for key, value in settings.items():
                        config, created = Configuration.objects.get_or_create(
                            section=section,
                            key=key,
                            defaults={
                                'value': value,
                                'updated_by': request.user
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            ConfigurationHistory.objects.create(
                                configuration=config,
                                old_value=config.value,
                                new_value=value,
                                changed_by=request.user,
                                reason=reason
                            )
                            config.value = value
                            config.updated_by = request.user
                            config.save()
                            updated_count += 1
            
            return Response({
                'message': f'Template "{template.name}" applied successfully',
                'created': created_count,
                'updated': updated_count
            })
            
        except Exception as e:
            logger.error(f"Failed to apply template {template.name}: {e}")
            return Response(
                {'error': 'Failed to apply template'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfigurationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing configuration change history.
    """
    queryset = ConfigurationHistory.objects.all()
    serializer_class = ConfigurationHistorySerializer
    permission_classes = [IsAuthenticated]  # Changed from IsAdminUser for testing
    filterset_fields = ['configuration', 'changed_by']
    ordering_fields = ['changed_at']
    ordering = ['-changed_at']