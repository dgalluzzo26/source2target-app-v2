"""
Serializers for the mapping app.

This module defines DRF serializers for field mapping functionality,
including source table discovery, target schema management, and
field mapping operations.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    SourceTable, SourceColumn, TargetSchema, TargetField,
    FieldMapping, MappingTemplate, MappingSession, AIMapping
)

User = get_user_model()


class SourceColumnSerializer(serializers.ModelSerializer):
    """
    Serializer for source columns.
    """
    full_column_name = serializers.ReadOnlyField()
    mapping_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SourceColumn
        fields = (
            'id', 'column_name', 'column_position', 'data_type',
            'physical_data_type', 'is_nullable', 'is_primary_key',
            'is_foreign_key', 'null_count', 'distinct_count',
            'min_value', 'max_value', 'avg_length', 'column_comment',
            'business_description', 'sample_values', 'full_column_name',
            'mapping_count', 'discovered_at', 'last_updated'
        )
        read_only_fields = ('id', 'discovered_at', 'last_updated')
    
    def get_mapping_count(self, obj):
        return obj.mappings.count()


class SourceTableSerializer(serializers.ModelSerializer):
    """
    Serializer for source tables.
    """
    columns = SourceColumnSerializer(many=True, read_only=True)
    column_count = serializers.ReadOnlyField()
    mapped_column_count = serializers.ReadOnlyField()
    mapping_progress = serializers.ReadOnlyField()
    discovered_by_name = serializers.CharField(source='discovered_by.display_name', read_only=True)
    
    class Meta:
        model = SourceTable
        fields = (
            'id', 'catalog_name', 'schema_name', 'table_name',
            'full_table_name', 'table_type', 'table_format', 'location',
            'owner', 'source_owners', 'row_count', 'size_bytes',
            'discovered_by', 'discovered_by_name', 'discovered_at',
            'last_updated', 'last_analyzed', 'is_active', 'analysis_status',
            'columns', 'column_count', 'mapped_column_count', 'mapping_progress'
        )
        read_only_fields = (
            'id', 'discovered_by', 'discovered_at', 'last_updated',
            'column_count', 'mapped_column_count', 'mapping_progress'
        )


class SourceTableSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for source table listings.
    """
    column_count = serializers.ReadOnlyField()
    mapped_column_count = serializers.ReadOnlyField()
    mapping_progress = serializers.ReadOnlyField()
    
    class Meta:
        model = SourceTable
        fields = (
            'id', 'catalog_name', 'schema_name', 'table_name',
            'full_table_name', 'table_type', 'owner', 'row_count',
            'column_count', 'mapped_column_count', 'mapping_progress',
            'discovered_at', 'last_analyzed', 'analysis_status'
        )


class TargetFieldSerializer(serializers.ModelSerializer):
    """
    Serializer for target fields.
    """
    mapping_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TargetField
        fields = (
            'id', 'field_name', 'field_path', 'data_type', 'is_required',
            'is_primary_key', 'field_description', 'business_rules',
            'example_values', 'validation_rules', 'mapping_count',
            'created_at', 'updated_at', 'is_active'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_mapping_count(self, obj):
        return obj.mappings.count()


class TargetSchemaSerializer(serializers.ModelSerializer):
    """
    Serializer for target schemas.
    """
    fields = TargetFieldSerializer(many=True, read_only=True)
    field_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)
    
    class Meta:
        model = TargetSchema
        fields = (
            'id', 'schema_name', 'display_name', 'description',
            'version', 'schema_type', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'is_active', 'fields', 'field_count'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')
    
    def get_field_count(self, obj):
        return obj.fields.count()


class TargetSchemaSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for target schema listings.
    """
    field_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TargetSchema
        fields = (
            'id', 'schema_name', 'display_name', 'description',
            'version', 'schema_type', 'field_count', 'created_at', 'is_active'
        )
    
    def get_field_count(self, obj):
        return obj.fields.count()


class FieldMappingSerializer(serializers.ModelSerializer):
    """
    Serializer for field mappings.
    """
    source_column_name = serializers.CharField(source='source_column.column_name', read_only=True)
    source_table_name = serializers.CharField(source='source_column.table.full_table_name', read_only=True)
    source_data_type = serializers.CharField(source='source_column.data_type', read_only=True)
    target_field_name = serializers.CharField(source='target_field.field_name', read_only=True)
    target_schema_name = serializers.CharField(source='target_field.schema.schema_name', read_only=True)
    target_data_type = serializers.CharField(source='target_field.data_type', read_only=True)
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)
    validated_by_name = serializers.CharField(source='validated_by.display_name', read_only=True)
    
    class Meta:
        model = FieldMapping
        fields = (
            'id', 'source_column', 'target_field', 'mapping_type',
            'transformation_logic', 'transformation_language',
            'confidence_score', 'is_validated', 'validation_notes',
            'suggested_by_ai', 'ai_reasoning', 'ai_model_version',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'validated_by', 'validated_by_name', 'validated_at', 'status',
            'source_column_name', 'source_table_name', 'source_data_type',
            'target_field_name', 'target_schema_name', 'target_data_type'
        )
        read_only_fields = (
            'id', 'created_by', 'created_at', 'updated_at',
            'validated_by', 'validated_at'
        )
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class FieldMappingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating field mappings.
    """
    
    class Meta:
        model = FieldMapping
        fields = (
            'source_column', 'target_field', 'mapping_type',
            'transformation_logic', 'transformation_language',
            'confidence_score', 'suggested_by_ai', 'ai_reasoning',
            'ai_model_version'
        )
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class FieldMappingValidationSerializer(serializers.Serializer):
    """
    Serializer for validating field mappings.
    """
    validation_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_mapping(self, mapping, user):
        """Validate the mapping with the provided notes."""
        notes = self.validated_data.get('validation_notes', '')
        mapping.validate_mapping(user, notes)
        return mapping


class AIMappingSerializer(serializers.ModelSerializer):
    """
    Serializer for AI mapping suggestions.
    """
    source_column_name = serializers.CharField(source='source_column.column_name', read_only=True)
    source_table_name = serializers.CharField(source='source_column.table.full_table_name', read_only=True)
    source_data_type = serializers.CharField(source='source_column.data_type', read_only=True)
    source_comment = serializers.CharField(source='source_column.column_comment', read_only=True)
    target_field_name = serializers.CharField(source='target_field.field_name', read_only=True)
    target_schema_name = serializers.CharField(source='target_field.schema.schema_name', read_only=True)
    target_data_type = serializers.CharField(source='target_field.data_type', read_only=True)
    target_description = serializers.CharField(source='target_field.field_description', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.display_name', read_only=True)
    
    class Meta:
        model = AIMapping
        fields = (
            'id', 'source_column', 'target_field', 'model_name',
            'model_version', 'confidence_score', 'reasoning',
            'similarity_score', 'context_used', 'status',
            'user_feedback', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'created_at', 'updated_at',
            'source_column_name', 'source_table_name', 'source_data_type',
            'source_comment', 'target_field_name', 'target_schema_name',
            'target_data_type', 'target_description'
        )
        read_only_fields = (
            'id', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at'
        )


class MappingTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for mapping templates.
    """
    created_by_name = serializers.CharField(source='created_by.display_name', read_only=True)
    target_schema_name = serializers.CharField(source='target_schema.display_name', read_only=True)
    
    class Meta:
        model = MappingTemplate
        fields = (
            'id', 'name', 'description', 'source_schema_pattern',
            'target_schema', 'target_schema_name', 'mapping_rules',
            'transformation_templates', 'usage_count', 'success_rate',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'is_active'
        )
        read_only_fields = (
            'id', 'created_by', 'usage_count', 'success_rate',
            'created_at', 'updated_at'
        )
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MappingSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for mapping sessions.
    """
    user_name = serializers.CharField(source='user.display_name', read_only=True)
    target_schema_name = serializers.CharField(source='target_schema.display_name', read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    source_table_names = serializers.SerializerMethodField()
    
    class Meta:
        model = MappingSession
        fields = (
            'id', 'user', 'user_name', 'session_name', 'source_tables',
            'source_table_names', 'target_schema', 'target_schema_name',
            'total_columns', 'mapped_columns', 'validated_mappings',
            'completion_percentage', 'notes', 'tags', 'created_at',
            'updated_at', 'completed_at', 'status'
        )
        read_only_fields = (
            'id', 'user', 'total_columns', 'mapped_columns',
            'validated_mappings', 'completion_percentage',
            'created_at', 'updated_at'
        )
    
    def get_source_table_names(self, obj):
        return [table.full_table_name for table in obj.source_tables.all()]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        source_tables = validated_data.pop('source_tables', [])
        session = super().create(validated_data)
        session.source_tables.set(source_tables)
        session.update_progress()
        return session


class BulkMappingSerializer(serializers.Serializer):
    """
    Serializer for bulk mapping operations.
    """
    mappings = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=1000
    )
    template_id = serializers.IntegerField(required=False)
    auto_validate = serializers.BooleanField(default=False)
    
    def validate_mappings(self, value):
        """Validate the mapping data structure."""
        required_fields = ['source_column_id', 'target_field_id']
        
        for i, mapping in enumerate(value):
            for field in required_fields:
                if field not in mapping:
                    raise serializers.ValidationError(
                        f"Mapping {i+1}: Missing required field '{field}'"
                    )
        
        return value


class MappingStatsSerializer(serializers.Serializer):
    """
    Serializer for mapping statistics.
    """
    total_tables = serializers.IntegerField()
    total_columns = serializers.IntegerField()
    mapped_columns = serializers.IntegerField()
    validated_mappings = serializers.IntegerField()
    ai_suggestions = serializers.IntegerField()
    mapping_progress = serializers.FloatField()
    recent_activity = serializers.ListField()
    
    # Progress by schema
    schema_progress = serializers.DictField()
    
    # Top contributors
    top_mappers = serializers.ListField()
    
    # AI performance
    ai_accuracy = serializers.FloatField()
    ai_usage_rate = serializers.FloatField()
