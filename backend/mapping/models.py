"""
Models for the field mapping functionality.

This module defines the data models for:
- Source table and column discovery
- Target schema definitions
- Field mappings between source and target
- AI-generated mapping suggestions
- Template upload/download functionality
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json

User = get_user_model()


class SourceTable(models.Model):
    """
    Represents a source table discovered from Databricks.
    """
    
    # Table identification
    catalog_name = models.CharField(max_length=255)
    schema_name = models.CharField(max_length=255)
    table_name = models.CharField(max_length=255)
    full_table_name = models.CharField(max_length=765, unique=True)  # catalog.schema.table
    
    # Table metadata
    table_type = models.CharField(
        max_length=50,
        choices=[
            ('TABLE', 'Table'),
            ('VIEW', 'View'),
            ('EXTERNAL', 'External Table'),
            ('TEMPORARY', 'Temporary Table'),
        ],
        default='TABLE'
    )
    table_format = models.CharField(max_length=50, blank=True, null=True)  # DELTA, PARQUET, etc.
    location = models.TextField(blank=True, null=True)
    
    # Ownership and access
    owner = models.CharField(max_length=255, blank=True, null=True)
    source_owners = models.TextField(
        blank=True, 
        null=True,
        help_text="Comma-separated list of users who can access this table"
    )
    
    # Table statistics
    row_count = models.BigIntegerField(null=True, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    
    # Discovery metadata
    discovered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_analyzed = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Analysis'),
            ('analyzing', 'Analyzing'),
            ('completed', 'Analysis Complete'),
            ('failed', 'Analysis Failed'),
        ],
        default='pending'
    )
    
    class Meta:
        db_table = 'mapping_source_tables'
        verbose_name = 'Source Table'
        verbose_name_plural = 'Source Tables'
        ordering = ['catalog_name', 'schema_name', 'table_name']
        indexes = [
            models.Index(fields=['catalog_name', 'schema_name']),
            models.Index(fields=['full_table_name']),
            models.Index(fields=['discovered_at']),
        ]
    
    def __str__(self):
        return self.full_table_name
    
    @property
    def column_count(self):
        return self.columns.count()
    
    @property
    def mapped_column_count(self):
        return self.columns.filter(mappings__isnull=False).distinct().count()
    
    @property
    def mapping_progress(self):
        total = self.column_count
        if total == 0:
            return 0
        mapped = self.mapped_column_count
        return round((mapped / total) * 100, 1)


class SourceColumn(models.Model):
    """
    Represents a column in a source table.
    """
    
    # Column identification
    table = models.ForeignKey(SourceTable, on_delete=models.CASCADE, related_name='columns')
    column_name = models.CharField(max_length=255)
    column_position = models.IntegerField()
    
    # Column metadata
    data_type = models.CharField(max_length=100)
    physical_data_type = models.CharField(max_length=100, blank=True, null=True)
    is_nullable = models.BooleanField(default=True)
    is_primary_key = models.BooleanField(default=False)
    is_foreign_key = models.BooleanField(default=False)
    
    # Column statistics
    null_count = models.BigIntegerField(null=True, blank=True)
    distinct_count = models.BigIntegerField(null=True, blank=True)
    min_value = models.TextField(null=True, blank=True)
    max_value = models.TextField(null=True, blank=True)
    avg_length = models.FloatField(null=True, blank=True)
    
    # Documentation
    column_comment = models.TextField(blank=True, null=True)
    business_description = models.TextField(blank=True, null=True)
    
    # Sample data (JSON field for flexibility)
    sample_values = models.JSONField(default=list, blank=True)
    
    # Discovery metadata
    discovered_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mapping_source_columns'
        verbose_name = 'Source Column'
        verbose_name_plural = 'Source Columns'
        ordering = ['table', 'column_position']
        unique_together = ['table', 'column_name']
        indexes = [
            models.Index(fields=['table', 'column_position']),
            models.Index(fields=['data_type']),
        ]
    
    def __str__(self):
        return f"{self.table.full_table_name}.{self.column_name}"
    
    @property
    def full_column_name(self):
        return f"{self.table.full_table_name}.{self.column_name}"


class TargetSchema(models.Model):
    """
    Represents a target schema/table structure for mapping.
    """
    
    # Schema identification
    schema_name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Schema metadata
    version = models.CharField(max_length=50, default='1.0')
    schema_type = models.CharField(
        max_length=50,
        choices=[
            ('semantic', 'Semantic Layer'),
            ('dimensional', 'Dimensional Model'),
            ('normalized', 'Normalized Schema'),
            ('custom', 'Custom Schema'),
        ],
        default='semantic'
    )
    
    # Management
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'mapping_target_schemas'
        verbose_name = 'Target Schema'
        verbose_name_plural = 'Target Schemas'
        ordering = ['schema_name']
    
    def __str__(self):
        return self.display_name or self.schema_name


class TargetField(models.Model):
    """
    Represents a field in the target schema.
    """
    
    # Field identification
    schema = models.ForeignKey(TargetSchema, on_delete=models.CASCADE, related_name='fields')
    field_name = models.CharField(max_length=255)
    field_path = models.CharField(max_length=500)  # For nested structures
    
    # Field metadata
    data_type = models.CharField(max_length=100)
    is_required = models.BooleanField(default=False)
    is_primary_key = models.BooleanField(default=False)
    
    # Documentation
    field_description = models.TextField(blank=True, null=True)
    business_rules = models.TextField(blank=True, null=True)
    example_values = models.JSONField(default=list, blank=True)
    
    # Validation rules
    validation_rules = models.JSONField(default=dict, blank=True)
    
    # Management
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'mapping_target_fields'
        verbose_name = 'Target Field'
        verbose_name_plural = 'Target Fields'
        ordering = ['schema', 'field_name']
        unique_together = ['schema', 'field_name']
    
    def __str__(self):
        return f"{self.schema.schema_name}.{self.field_name}"


class FieldMapping(models.Model):
    """
    Represents a mapping between source columns and target fields.
    """
    
    # Mapping identification
    source_column = models.ForeignKey(SourceColumn, on_delete=models.CASCADE, related_name='mappings')
    target_field = models.ForeignKey(TargetField, on_delete=models.CASCADE, related_name='mappings')
    
    # Mapping metadata
    mapping_type = models.CharField(
        max_length=20,
        choices=[
            ('direct', 'Direct Mapping'),
            ('transformed', 'Transformed Mapping'),
            ('calculated', 'Calculated Field'),
            ('lookup', 'Lookup Mapping'),
            ('conditional', 'Conditional Mapping'),
        ],
        default='direct'
    )
    
    # Transformation logic
    transformation_logic = models.TextField(blank=True, null=True)
    transformation_language = models.CharField(
        max_length=20,
        choices=[
            ('sql', 'SQL'),
            ('python', 'Python'),
            ('spark', 'Spark SQL'),
            ('custom', 'Custom Logic'),
        ],
        default='sql'
    )
    
    # Mapping confidence and validation
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True,
        blank=True,
        help_text="AI confidence score for this mapping (0.0 to 1.0)"
    )
    is_validated = models.BooleanField(default=False)
    validation_notes = models.TextField(blank=True, null=True)
    
    # AI suggestion metadata
    suggested_by_ai = models.BooleanField(default=False)
    ai_reasoning = models.TextField(blank=True, null=True)
    ai_model_version = models.CharField(max_length=100, blank=True, null=True)
    
    # Management
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='validated_mappings'
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('pending_review', 'Pending Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('archived', 'Archived'),
        ],
        default='draft'
    )
    
    class Meta:
        db_table = 'mapping_field_mappings'
        verbose_name = 'Field Mapping'
        verbose_name_plural = 'Field Mappings'
        ordering = ['-created_at']
        unique_together = ['source_column', 'target_field']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['suggested_by_ai']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.source_column} → {self.target_field}"
    
    def validate_mapping(self, user, notes=None):
        """Mark this mapping as validated."""
        self.is_validated = True
        self.validated_by = user
        self.validated_at = timezone.now()
        self.status = 'approved'
        if notes:
            self.validation_notes = notes
        self.save()


class MappingTemplate(models.Model):
    """
    Represents a template for bulk mapping operations.
    """
    
    # Template identification
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Template metadata
    source_schema_pattern = models.CharField(max_length=255, blank=True, null=True)
    target_schema = models.ForeignKey(TargetSchema, on_delete=models.CASCADE, related_name='templates')
    
    # Template data (JSON structure)
    mapping_rules = models.JSONField(default=dict)
    transformation_templates = models.JSONField(default=dict)
    
    # Usage statistics
    usage_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    # Management
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'mapping_templates'
        verbose_name = 'Mapping Template'
        verbose_name_plural = 'Mapping Templates'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class MappingSession(models.Model):
    """
    Represents a user's mapping session for tracking progress.
    """
    
    # Session identification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mapping_sessions')
    session_name = models.CharField(max_length=255)
    
    # Session scope
    source_tables = models.ManyToManyField(SourceTable, blank=True)
    target_schema = models.ForeignKey(TargetSchema, on_delete=models.CASCADE)
    
    # Session progress
    total_columns = models.IntegerField(default=0)
    mapped_columns = models.IntegerField(default=0)
    validated_mappings = models.IntegerField(default=0)
    
    # Session metadata
    notes = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Management
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('completed', 'Completed'),
            ('archived', 'Archived'),
        ],
        default='active'
    )
    
    class Meta:
        db_table = 'mapping_sessions'
        verbose_name = 'Mapping Session'
        verbose_name_plural = 'Mapping Sessions'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.session_name}"
    
    @property
    def completion_percentage(self):
        if self.total_columns == 0:
            return 0
        return round((self.mapped_columns / self.total_columns) * 100, 1)
    
    def update_progress(self):
        """Update session progress based on current mappings."""
        # Count total columns in source tables
        total = sum(table.column_count for table in self.source_tables.all())
        
        # Count mapped columns
        mapped = FieldMapping.objects.filter(
            source_column__table__in=self.source_tables.all(),
            target_field__schema=self.target_schema
        ).count()
        
        # Count validated mappings
        validated = FieldMapping.objects.filter(
            source_column__table__in=self.source_tables.all(),
            target_field__schema=self.target_schema,
            is_validated=True
        ).count()
        
        self.total_columns = total
        self.mapped_columns = mapped
        self.validated_mappings = validated
        self.save()


class AIMapping(models.Model):
    """
    Stores AI-generated mapping suggestions for analysis and improvement.
    """
    
    # AI suggestion identification
    source_column = models.ForeignKey(SourceColumn, on_delete=models.CASCADE, related_name='ai_suggestions')
    target_field = models.ForeignKey(TargetField, on_delete=models.CASCADE, related_name='ai_suggestions')
    
    # AI metadata
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50)
    confidence_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # AI reasoning
    reasoning = models.TextField()
    similarity_score = models.FloatField(null=True, blank=True)
    context_used = models.JSONField(default=dict)
    
    # Suggestion status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Review'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('modified', 'Modified'),
        ],
        default='pending'
    )
    
    # User feedback
    user_feedback = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Management
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mapping_ai_suggestions'
        verbose_name = 'AI Mapping Suggestion'
        verbose_name_plural = 'AI Mapping Suggestions'
        ordering = ['-confidence_score', '-created_at']
        indexes = [
            models.Index(fields=['confidence_score']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"AI: {self.source_column} → {self.target_field} ({self.confidence_score:.2f})"