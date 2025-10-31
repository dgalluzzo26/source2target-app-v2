"""
Serializers for configuration management.
"""

from rest_framework import serializers
from .models import Configuration, ConfigurationHistory, ConfigurationTemplate, get_default_configuration


class ConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for individual configuration settings."""
    
    class Meta:
        model = Configuration
        fields = [
            'id', 'section', 'key', 'value', 'description', 
            'is_active', 'created_at', 'updated_at', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConfigurationHistorySerializer(serializers.ModelSerializer):
    """Serializer for configuration change history."""
    
    class Meta:
        model = ConfigurationHistory
        fields = [
            'id', 'configuration', 'old_value', 'new_value',
            'changed_by', 'changed_at', 'reason'
        ]
        read_only_fields = ['id', 'changed_at']


class ConfigurationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for configuration templates."""
    
    class Meta:
        model = ConfigurationTemplate
        fields = [
            'id', 'name', 'description', 'configuration_data',
            'is_default', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConfigurationSectionSerializer(serializers.Serializer):
    """Serializer for a complete configuration section."""
    
    section = serializers.CharField()
    settings = serializers.DictField()


class FullConfigurationSerializer(serializers.Serializer):
    """Serializer for the complete application configuration."""
    
    database = serializers.DictField()
    ai_model = serializers.DictField()
    ui = serializers.DictField()
    support = serializers.DictField()
    vector_search = serializers.DictField()
    security = serializers.DictField()


class ConfigurationUpdateSerializer(serializers.Serializer):
    """Serializer for updating configuration settings."""
    
    section = serializers.CharField()
    key = serializers.CharField()
    value = serializers.JSONField()
    reason = serializers.CharField(required=False, allow_blank=True)


class ConfigurationBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk configuration updates."""
    
    configuration = serializers.DictField()
    reason = serializers.CharField(required=False, allow_blank=True)


class ConfigurationTestSerializer(serializers.Serializer):
    """Serializer for configuration testing requests."""
    
    test_type = serializers.ChoiceField(choices=[
        ('database', 'Database Connection'),
        ('vector_search', 'Vector Search'),
        ('ai_model', 'AI Model'),
    ])
    configuration = serializers.DictField(required=False)


class ConfigurationExportSerializer(serializers.Serializer):
    """Serializer for configuration export."""
    
    include_sections = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of sections to include in export. If empty, all sections are included."
    )
    format = serializers.ChoiceField(
        choices=[('json', 'JSON'), ('yaml', 'YAML')],
        default='json'
    )


class ConfigurationImportSerializer(serializers.Serializer):
    """Serializer for configuration import."""
    
    configuration_data = serializers.JSONField()
    merge_strategy = serializers.ChoiceField(
        choices=[
            ('replace', 'Replace All'),
            ('merge', 'Merge with Existing'),
            ('update', 'Update Only Existing Keys')
        ],
        default='merge'
    )
    reason = serializers.CharField(required=False, allow_blank=True)
