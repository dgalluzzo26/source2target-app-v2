"""
Configuration models for the Source-to-Target Mapping Platform.

This module defines models for managing application configuration settings,
including database connections, AI model parameters, UI preferences, and security settings.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class ConfigurationSection(models.TextChoices):
    """Configuration section choices."""
    DATABASE = 'database', 'Database'
    AI_MODEL = 'ai_model', 'AI Model'
    UI = 'ui', 'UI Settings'
    SUPPORT = 'support', 'Support'
    VECTOR_SEARCH = 'vector_search', 'Vector Search'
    SECURITY = 'security', 'Security'


class Configuration(models.Model):
    """
    Application configuration model.
    
    Stores configuration settings in a flexible JSON format organized by sections.
    Each configuration entry has a section, key, and value.
    """
    section = models.CharField(
        max_length=50,
        choices=ConfigurationSection.choices,
        help_text="Configuration section"
    )
    key = models.CharField(
        max_length=100,
        help_text="Configuration key within the section"
    )
    value = models.JSONField(
        help_text="Configuration value (can be any JSON-serializable type)"
    )
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of this configuration setting"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this configuration setting is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who last updated this configuration"
    )

    class Meta:
        unique_together = ['section', 'key']
        ordering = ['section', 'key']
        indexes = [
            models.Index(fields=['section']),
            models.Index(fields=['section', 'key']),
        ]

    def __str__(self):
        return f"{self.section}.{self.key}"


class ConfigurationHistory(models.Model):
    """
    Configuration change history.
    
    Tracks changes to configuration settings for audit purposes.
    """
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_value = models.JSONField(
        null=True,
        blank=True,
        help_text="Previous configuration value"
    )
    new_value = models.JSONField(
        help_text="New configuration value"
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(
        blank=True,
        help_text="Reason for the configuration change"
    )

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.configuration} changed at {self.changed_at}"


class ConfigurationTemplate(models.Model):
    """
    Configuration templates for different environments or use cases.
    
    Allows saving and loading complete configuration sets.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Template name"
    )
    description = models.TextField(
        blank=True,
        help_text="Template description"
    )
    configuration_data = models.JSONField(
        help_text="Complete configuration data as JSON"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default template"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one default template
        if self.is_default:
            ConfigurationTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


def get_default_configuration():
    """
    Get the default configuration structure.
    
    Returns the same structure as the original Streamlit app's ConfigManager.
    """
    return {
        "database": {
            "warehouse_name": "gia-oztest-dev-data-warehouse",
            "mapping_table": "oztest_dev.source_to_target.mappings",
            "semantic_table": "oztest_dev.source_to_target.silver_semantic_full",
            "server_hostname": "Acuity-oz-test-ue1.cloud.databricks.com",
            "http_path": "/sql/1.0/warehouses/173ea239ed13be7d"
        },
        "ai_model": {
            "previous_mappings_table_name": "oztest_dev.source_to_target.train_with_comments",
            "foundation_model_endpoint": "databricks-meta-llama-3-3-70b-instruct",
            "default_prompt": """You are a ETL engineer and your job is to take in information on an incoming field from a source database and map it to an existing target table in your database.{feedback_section}{previous_section}

The incoming field can be described by its table name, column name, natural language desription, whether or not it is nullable, and its datatype. The same information from semantically similar fields in your target database table field are provided in this prompt, and it is likely that one of these provided columns is the correct match for mapping. As an additional hint, each target field may contain source fields that have been previously mapped to that target field. The semantically similar target fields (and their corresponding previous source field mappings) can be found in this structure:

{retrieved_context_structure}

If no previous data has been mapped to the target_table_field, you will see an [NaN]. Here is the information about the target table and its columns:

{retrieved_context}

Here is the source field you want to map to one of those target columns: {query_text}{no_mapping_guidance}

Please return your top {num_results} guesses for the correct target column mapping, in order. IMPORTANT: Your suggestions must comply with any constraints specified above. Do not include any mappings that violate the user requirements or include excluded columns. Format your response in a json format with a "results" key containing array of the results (i.e. 
```{results_structure}```
). The "reasoning" field should contain a brief description of why you think this mapping is correct and confirm it meets the specified constraints. You can include references to previously mapped columns or semantic or datatype similiarities."""
        },
        "ui": {
            "app_title": "Source-to-Target Mapping Platform",
            "theme_color": "#4a5568",
            "sidebar_expanded": True
        },
        "support": {
            "support_url": "https://mygainwell.sharepoint.com"
        },
        "vector_search": {
            "index_name": "oztest_dev.source_to_target.silver_semantic_full_vs",
            "endpoint_name": "s2t_vsendpoint"
        },
        "security": {
            "admin_group_name": "gia-oztest-dev-ue1-data-engineers",
            "enable_password_auth": True,
            "admin_password_hash": ""
        }
    }