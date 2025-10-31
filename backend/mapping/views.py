"""
API views for field mapping functionality.

This module provides REST API endpoints for:
- Source table and column discovery
- Target schema management
- Field mapping operations
- AI-powered mapping suggestions
- Template management and bulk operations
"""

from rest_framework import generics, viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from accounts.permissions import IsAdminUser, CanAccessMapping, ReadOnlyOrAdmin
from .models import (
    SourceTable, SourceColumn, TargetSchema, TargetField,
    FieldMapping, MappingTemplate, MappingSession, AIMapping
)
from .serializers import (
    SourceTableSerializer, SourceTableSummarySerializer, SourceColumnSerializer,
    TargetSchemaSerializer, TargetSchemaSummarySerializer, TargetFieldSerializer,
    FieldMappingSerializer, FieldMappingCreateSerializer, FieldMappingValidationSerializer,
    AIMappingSerializer, MappingTemplateSerializer, MappingSessionSerializer,
    BulkMappingSerializer, MappingStatsSerializer
)
from .services.databricks_service import databricks_service, DatabricksConnectionError
from .services.discovery_service import discovery_service


class SourceTableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing source tables.
    """
    queryset = SourceTable.objects.all()
    permission_classes = [CanAccessMapping]
    filterset_fields = ['catalog_name', 'schema_name', 'table_type', 'analysis_status', 'is_active']
    search_fields = ['table_name', 'full_table_name', 'owner']
    ordering_fields = ['table_name', 'discovered_at', 'row_count', 'mapping_progress']
    ordering = ['-discovered_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SourceTableSummarySerializer
        return SourceTableSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user access if source_owners is set
        user_email = self.request.user.email
        if not self.request.user.is_admin:
            queryset = queryset.filter(
                Q(source_owners__isnull=True) | 
                Q(source_owners__icontains=user_email)
            )
        
        return queryset
    
    @extend_schema(
        summary="List source tables",
        description="Get a list of discovered source tables with filtering and search",
        parameters=[
            OpenApiParameter('catalog_name', OpenApiTypes.STR, description='Filter by catalog'),
            OpenApiParameter('schema_name', OpenApiTypes.STR, description='Filter by schema'),
            OpenApiParameter('table_type', OpenApiTypes.STR, description='Filter by table type'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search in table name and owner'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get table details",
        description="Get detailed information about a specific source table including columns",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get table columns",
        description="Get all columns for a specific source table",
    )
    @action(detail=True, methods=['get'])
    def columns(self, request, pk=None):
        table = self.get_object()
        columns = table.columns.all().order_by('column_position')
        serializer = SourceColumnSerializer(columns, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get table mappings",
        description="Get all field mappings for columns in this table",
    )
    @action(detail=True, methods=['get'])
    def mappings(self, request, pk=None):
        table = self.get_object()
        mappings = FieldMapping.objects.filter(source_column__table=table)
        serializer = FieldMappingSerializer(mappings, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Analyze table",
        description="Trigger analysis of table structure and statistics",
    )
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        table = self.get_object()

        try:
            # Update table analysis status
            table.analysis_status = 'analyzing'
            table.last_analyzed = timezone.now()
            table.save()

            # Refresh table statistics using Databricks service
            success = discovery_service.refresh_table_statistics(table)
            
            if success:
                return Response({
                    'message': f'Analysis completed for table {table.full_table_name}',
                    'status': table.analysis_status
                })
            else:
                return Response({
                    'message': f'Analysis failed for table {table.full_table_name}',
                    'status': table.analysis_status
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            table.analysis_status = 'failed'
            table.save()
            return Response({
                'error': f'Analysis failed: {str(e)}',
                'status': table.analysis_status
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Discover tables from Databricks",
        description="Discover and sync tables from Databricks catalogs",
        parameters=[
            OpenApiParameter('catalogs', OpenApiTypes.STR, description='Comma-separated list of catalogs to search'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search term for table names'),
        ]
    )
    @action(detail=False, methods=['post'])
    def discover(self, request):
        """Discover tables from Databricks and sync them to the database."""
        try:
            catalogs = request.data.get('catalogs')
            search_term = request.data.get('search')
            
            if catalogs:
                catalogs = [cat.strip() for cat in catalogs.split(',')]
            
            if search_term:
                # Search for specific tables
                stats = discovery_service.search_and_sync_tables(
                    request.user, search_term, catalogs
                )
            else:
                # Discover all tables in specified catalogs
                stats = discovery_service.discover_all_tables(request.user, catalogs)
            
            return Response({
                'message': 'Table discovery completed',
                'stats': stats
            })
            
        except DatabricksConnectionError as e:
            return Response({
                'error': f'Databricks connection failed: {str(e)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            logger.error(f"Table discovery failed: {e}")
            return Response({
                'error': f'Discovery failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Test Databricks connection",
        description="Test the connection to Databricks services",
    )
    @action(detail=False, methods=['get'])
    def test_connection(self, request):
        """Test Databricks connection."""
        try:
            connection_status = databricks_service.test_connection()
            
            if connection_status['overall_status']:
                return Response({
                    'message': 'Databricks connection successful',
                    'details': connection_status
                })
            else:
                return Response({
                    'message': 'Databricks connection failed',
                    'details': connection_status
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            return Response({
                'error': f'Connection test failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TargetSchemaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing target schemas.
    """
    queryset = TargetSchema.objects.filter(is_active=True)
    permission_classes = [CanAccessMapping]
    filterset_fields = ['schema_type', 'is_active']
    search_fields = ['schema_name', 'display_name', 'description']
    ordering_fields = ['schema_name', 'created_at']
    ordering = ['schema_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TargetSchemaSummarySerializer
        return TargetSchemaSerializer
    
    @extend_schema(
        summary="List target schemas",
        description="Get a list of available target schemas for mapping",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get schema details",
        description="Get detailed information about a target schema including fields",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get schema fields",
        description="Get all fields for a specific target schema",
    )
    @action(detail=True, methods=['get'])
    def fields(self, request, pk=None):
        schema = self.get_object()
        fields = schema.fields.filter(is_active=True).order_by('field_name')
        serializer = TargetFieldSerializer(fields, many=True)
        return Response(serializer.data)


class FieldMappingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing field mappings.
    """
    queryset = FieldMapping.objects.all()
    permission_classes = [CanAccessMapping]
    filterset_fields = ['mapping_type', 'status', 'suggested_by_ai', 'is_validated']
    search_fields = ['source_column__column_name', 'target_field__field_name']
    ordering_fields = ['created_at', 'confidence_score', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FieldMappingCreateSerializer
        return FieldMappingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user access
        user_email = self.request.user.email
        if not self.request.user.is_admin:
            queryset = queryset.filter(
                Q(source_column__table__source_owners__isnull=True) | 
                Q(source_column__table__source_owners__icontains=user_email) |
                Q(created_by=self.request.user)
            )
        
        return queryset
    
    @extend_schema(
        summary="List field mappings",
        description="Get a list of field mappings with filtering options",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create field mapping",
        description="Create a new field mapping between source and target",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        summary="Validate mapping",
        description="Mark a field mapping as validated",
    )
    @action(detail=True, methods=['post'])
    def validate_mapping(self, request, pk=None):
        mapping = self.get_object()
        serializer = FieldMappingValidationSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.validate_mapping(mapping, request.user)
            return Response({
                'message': 'Mapping validated successfully',
                'mapping': FieldMappingSerializer(mapping).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Bulk create mappings",
        description="Create multiple field mappings at once",
    )
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = BulkMappingSerializer(data=request.data)
        
        if serializer.is_valid():
            mappings_data = serializer.validated_data['mappings']
            auto_validate = serializer.validated_data.get('auto_validate', False)
            
            created_mappings = []
            errors = []
            
            for i, mapping_data in enumerate(mappings_data):
                try:
                    # Create individual mapping
                    mapping_serializer = FieldMappingCreateSerializer(
                        data=mapping_data,
                        context={'request': request}
                    )
                    
                    if mapping_serializer.is_valid():
                        mapping = mapping_serializer.save()
                        
                        if auto_validate:
                            mapping.validate_mapping(request.user)
                        
                        created_mappings.append(mapping)
                    else:
                        errors.append({
                            'index': i,
                            'errors': mapping_serializer.errors
                        })
                
                except Exception as e:
                    errors.append({
                        'index': i,
                        'error': str(e)
                    })
            
            return Response({
                'created_count': len(created_mappings),
                'error_count': len(errors),
                'mappings': FieldMappingSerializer(created_mappings, many=True).data,
                'errors': errors
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AIMappingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AI mapping suggestions (read-only).
    """
    queryset = AIMapping.objects.all()
    serializer_class = AIMappingSerializer
    permission_classes = [CanAccessMapping]
    filterset_fields = ['status', 'model_name']
    search_fields = ['source_column__column_name', 'target_field__field_name']
    ordering_fields = ['confidence_score', 'created_at']
    ordering = ['-confidence_score', '-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user access
        user_email = self.request.user.email
        if not self.request.user.is_admin:
            queryset = queryset.filter(
                Q(source_column__table__source_owners__isnull=True) | 
                Q(source_column__table__source_owners__icontains=user_email)
            )
        
        return queryset
    
    @extend_schema(
        summary="Accept AI suggestion",
        description="Accept an AI mapping suggestion and create a field mapping",
    )
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        ai_mapping = self.get_object()
        
        # Create field mapping from AI suggestion
        field_mapping = FieldMapping.objects.create(
            source_column=ai_mapping.source_column,
            target_field=ai_mapping.target_field,
            mapping_type='direct',
            confidence_score=ai_mapping.confidence_score,
            suggested_by_ai=True,
            ai_reasoning=ai_mapping.reasoning,
            ai_model_version=f"{ai_mapping.model_name}:{ai_mapping.model_version}",
            created_by=request.user
        )
        
        # Update AI suggestion status
        ai_mapping.status = 'accepted'
        ai_mapping.reviewed_by = request.user
        ai_mapping.reviewed_at = timezone.now()
        ai_mapping.save()
        
        return Response({
            'message': 'AI suggestion accepted and mapping created',
            'mapping': FieldMappingSerializer(field_mapping).data
        })
    
    @extend_schema(
        summary="Reject AI suggestion",
        description="Reject an AI mapping suggestion with optional feedback",
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        ai_mapping = self.get_object()
        
        ai_mapping.status = 'rejected'
        ai_mapping.user_feedback = request.data.get('feedback', '')
        ai_mapping.reviewed_by = request.user
        ai_mapping.reviewed_at = timezone.now()
        ai_mapping.save()
        
        return Response({
            'message': 'AI suggestion rejected',
            'suggestion': AIMappingSerializer(ai_mapping).data
        })


class MappingTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mapping templates.
    """
    queryset = MappingTemplate.objects.filter(is_active=True)
    serializer_class = MappingTemplateSerializer
    permission_classes = [CanAccessMapping]
    filterset_fields = ['target_schema', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'usage_count']
    ordering = ['-usage_count', 'name']
    
    @extend_schema(
        summary="Apply template",
        description="Apply a mapping template to create multiple mappings",
    )
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        template = self.get_object()
        
        # TODO: Implement template application logic
        # This would parse the template rules and create mappings
        
        template.usage_count += 1
        template.save()
        
        return Response({
            'message': f'Template "{template.name}" applied successfully',
            'template': MappingTemplateSerializer(template).data
        })


class MappingSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mapping sessions.
    """
    queryset = MappingSession.objects.all()
    serializer_class = MappingSessionSerializer
    permission_classes = [CanAccessMapping]
    filterset_fields = ['status', 'target_schema']
    search_fields = ['session_name', 'notes']
    ordering_fields = ['created_at', 'updated_at', 'completion_percentage']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        # Users can only see their own sessions unless they're admin
        if self.request.user.is_admin:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)
    
    @extend_schema(
        summary="Update session progress",
        description="Recalculate and update session progress statistics",
    )
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        session = self.get_object()
        session.update_progress()
        
        return Response({
            'message': 'Session progress updated',
            'session': MappingSessionSerializer(session).data
        })


@extend_schema(
    summary="Get mapping statistics",
    description="Get comprehensive mapping statistics and progress information",
    responses={200: MappingStatsSerializer}
)
@api_view(['GET'])
@permission_classes([CanAccessMapping])
def mapping_stats(request):
    """
    Get comprehensive mapping statistics.
    """
    user_email = request.user.email
    
    # Base querysets with user access filtering
    if request.user.is_admin:
        tables_qs = SourceTable.objects.filter(is_active=True)
        mappings_qs = FieldMapping.objects.all()
    else:
        tables_qs = SourceTable.objects.filter(
            is_active=True
        ).filter(
            Q(source_owners__isnull=True) | 
            Q(source_owners__icontains=user_email)
        )
        mappings_qs = FieldMapping.objects.filter(
            Q(source_column__table__source_owners__isnull=True) | 
            Q(source_column__table__source_owners__icontains=user_email) |
            Q(created_by=request.user)
        )
    
    # Calculate statistics
    total_tables = tables_qs.count()
    total_columns = SourceColumn.objects.filter(table__in=tables_qs).count()
    mapped_columns = mappings_qs.values('source_column').distinct().count()
    validated_mappings = mappings_qs.filter(is_validated=True).count()
    ai_suggestions = AIMapping.objects.filter(
        source_column__table__in=tables_qs
    ).count()
    
    mapping_progress = (mapped_columns / total_columns * 100) if total_columns > 0 else 0
    
    # Recent activity
    recent_mappings = mappings_qs.order_by('-created_at')[:10]
    recent_activity = [
        {
            'type': 'mapping_created',
            'description': f'Mapped {m.source_column.column_name} to {m.target_field.field_name}',
            'user': m.created_by.display_name if m.created_by else 'System',
            'timestamp': m.created_at
        }
        for m in recent_mappings
    ]
    
    # Schema progress
    schema_progress = {}
    for schema in TargetSchema.objects.filter(is_active=True):
        schema_mappings = mappings_qs.filter(target_field__schema=schema).count()
        schema_fields = schema.fields.count()
        progress = (schema_mappings / schema_fields * 100) if schema_fields > 0 else 0
        schema_progress[schema.schema_name] = {
            'mapped': schema_mappings,
            'total': schema_fields,
            'progress': round(progress, 1)
        }
    
    # Top contributors
    top_mappers = list(
        mappings_qs.values('created_by__display_name')
        .annotate(mapping_count=Count('id'))
        .order_by('-mapping_count')[:5]
    )
    
    # AI performance
    ai_mappings = AIMapping.objects.filter(source_column__table__in=tables_qs)
    ai_accepted = ai_mappings.filter(status='accepted').count()
    ai_total = ai_mappings.count()
    ai_accuracy = (ai_accepted / ai_total * 100) if ai_total > 0 else 0
    ai_usage_rate = (ai_suggestions / total_columns * 100) if total_columns > 0 else 0
    
    stats_data = {
        'total_tables': total_tables,
        'total_columns': total_columns,
        'mapped_columns': mapped_columns,
        'validated_mappings': validated_mappings,
        'ai_suggestions': ai_suggestions,
        'mapping_progress': round(mapping_progress, 1),
        'recent_activity': recent_activity,
        'schema_progress': schema_progress,
        'top_mappers': top_mappers,
        'ai_accuracy': round(ai_accuracy, 1),
        'ai_usage_rate': round(ai_usage_rate, 1)
    }
    
    serializer = MappingStatsSerializer(stats_data)
    return Response(serializer.data)
