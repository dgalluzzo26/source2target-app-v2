"""
Data discovery service for syncing Databricks metadata with Django models.

This service handles:
- Discovering and syncing source tables and columns
- Updating table and column metadata
- Managing discovery sessions and progress tracking
- Handling incremental updates and change detection
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from ..models import SourceTable, SourceColumn
from .databricks_service import databricks_service, DatabricksConnectionError

User = get_user_model()
logger = logging.getLogger(__name__)


class DiscoveryService:
    """
    Service for discovering and syncing data from Databricks.
    """
    
    def __init__(self):
        self.databricks = databricks_service
    
    def discover_all_tables(self, user: User, catalogs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Discover all tables from specified catalogs or all available catalogs.
        """
        try:
            discovery_stats = {
                'catalogs_processed': 0,
                'schemas_processed': 0,
                'tables_discovered': 0,
                'tables_created': 0,
                'tables_updated': 0,
                'columns_created': 0,
                'columns_updated': 0,
                'errors': []
            }
            
            # Get catalogs to process
            if not catalogs:
                try:
                    catalog_list = self.databricks.discover_catalogs()
                    catalogs = [cat['name'] for cat in catalog_list]
                except Exception as e:
                    logger.error(f"Failed to discover catalogs: {e}")
                    discovery_stats['errors'].append(f"Failed to discover catalogs: {e}")
                    return discovery_stats
            
            # Process each catalog
            for catalog_name in catalogs:
                try:
                    catalog_stats = self.discover_catalog_tables(user, catalog_name)
                    
                    # Aggregate stats
                    discovery_stats['schemas_processed'] += catalog_stats['schemas_processed']
                    discovery_stats['tables_discovered'] += catalog_stats['tables_discovered']
                    discovery_stats['tables_created'] += catalog_stats['tables_created']
                    discovery_stats['tables_updated'] += catalog_stats['tables_updated']
                    discovery_stats['columns_created'] += catalog_stats['columns_created']
                    discovery_stats['columns_updated'] += catalog_stats['columns_updated']
                    discovery_stats['errors'].extend(catalog_stats['errors'])
                    
                    discovery_stats['catalogs_processed'] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to process catalog {catalog_name}: {e}"
                    logger.error(error_msg)
                    discovery_stats['errors'].append(error_msg)
            
            logger.info(f"Discovery completed: {discovery_stats}")
            return discovery_stats
            
        except Exception as e:
            logger.error(f"Discovery process failed: {e}")
            discovery_stats['errors'].append(f"Discovery process failed: {e}")
            return discovery_stats
    
    def discover_catalog_tables(self, user: User, catalog_name: str) -> Dict[str, Any]:
        """
        Discover all tables in a specific catalog.
        """
        stats = {
            'schemas_processed': 0,
            'tables_discovered': 0,
            'tables_created': 0,
            'tables_updated': 0,
            'columns_created': 0,
            'columns_updated': 0,
            'errors': []
        }
        
        try:
            # Get schemas in catalog
            schemas = self.databricks.discover_schemas(catalog_name)
            
            for schema in schemas:
                try:
                    schema_stats = self.discover_schema_tables(user, catalog_name, schema['name'])
                    
                    # Aggregate stats
                    stats['tables_discovered'] += schema_stats['tables_discovered']
                    stats['tables_created'] += schema_stats['tables_created']
                    stats['tables_updated'] += schema_stats['tables_updated']
                    stats['columns_created'] += schema_stats['columns_created']
                    stats['columns_updated'] += schema_stats['columns_updated']
                    stats['errors'].extend(schema_stats['errors'])
                    
                    stats['schemas_processed'] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to process schema {catalog_name}.{schema['name']}: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
            
            return stats
            
        except Exception as e:
            error_msg = f"Failed to discover schemas in catalog {catalog_name}: {e}"
            logger.error(error_msg)
            stats['errors'].append(error_msg)
            return stats
    
    def discover_schema_tables(self, user: User, catalog_name: str, schema_name: str) -> Dict[str, Any]:
        """
        Discover all tables in a specific schema.
        """
        stats = {
            'tables_discovered': 0,
            'tables_created': 0,
            'tables_updated': 0,
            'columns_created': 0,
            'columns_updated': 0,
            'errors': []
        }
        
        try:
            # Get tables in schema
            tables = self.databricks.discover_tables(catalog_name, schema_name)
            
            for table_data in tables:
                try:
                    table_stats = self.sync_table(user, table_data)
                    
                    stats['tables_discovered'] += 1
                    if table_stats['created']:
                        stats['tables_created'] += 1
                    else:
                        stats['tables_updated'] += 1
                    
                    stats['columns_created'] += table_stats['columns_created']
                    stats['columns_updated'] += table_stats['columns_updated']
                    
                except Exception as e:
                    error_msg = f"Failed to sync table {table_data.get('full_name', 'unknown')}: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
            
            return stats
            
        except Exception as e:
            error_msg = f"Failed to discover tables in {catalog_name}.{schema_name}: {e}"
            logger.error(error_msg)
            stats['errors'].append(error_msg)
            return stats
    
    @transaction.atomic
    def sync_table(self, user: User, table_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync a single table with the database.
        """
        stats = {
            'created': False,
            'columns_created': 0,
            'columns_updated': 0
        }
        
        try:
            full_table_name = table_data['full_name']
            
            # Get or create the source table
            table, created = SourceTable.objects.get_or_create(
                full_table_name=full_table_name,
                defaults={
                    'catalog_name': table_data['catalog_name'],
                    'schema_name': table_data['schema_name'],
                    'table_name': table_data['name'],
                    'table_type': table_data.get('table_type', 'TABLE'),
                    'table_format': table_data.get('data_source_format', ''),
                    'location': table_data.get('storage_location', ''),
                    'owner': table_data.get('owner', ''),
                    'row_count': table_data.get('row_count', 0),
                    'size_bytes': table_data.get('size_bytes', 0),
                    'discovered_by': user,
                    'analysis_status': 'pending'
                }
            )
            
            stats['created'] = created
            
            # Update table if it already existed
            if not created:
                # Update fields that might have changed
                table.table_type = table_data.get('table_type', table.table_type)
                table.table_format = table_data.get('data_source_format', table.table_format)
                table.location = table_data.get('storage_location', table.location)
                table.owner = table_data.get('owner', table.owner)
                table.row_count = table_data.get('row_count', table.row_count)
                table.size_bytes = table_data.get('size_bytes', table.size_bytes)
                table.last_updated = timezone.now()
                table.save()
            
            # Discover and sync columns
            column_stats = self.sync_table_columns(table)
            stats['columns_created'] = column_stats['columns_created']
            stats['columns_updated'] = column_stats['columns_updated']
            
            # Update analysis status
            table.analysis_status = 'completed'
            table.last_analyzed = timezone.now()
            table.save()
            
            logger.info(f"Synced table {full_table_name}: created={created}, columns_created={column_stats['columns_created']}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to sync table {table_data.get('full_name', 'unknown')}: {e}")
            raise
    
    @transaction.atomic
    def sync_table_columns(self, table: SourceTable) -> Dict[str, Any]:
        """
        Sync columns for a specific table.
        """
        stats = {
            'columns_created': 0,
            'columns_updated': 0
        }
        
        try:
            # Discover columns from Databricks
            columns_data = self.databricks.discover_columns(
                table.catalog_name, 
                table.schema_name, 
                table.table_name
            )
            
            # Track existing columns to identify removed ones
            existing_columns = set(
                table.columns.values_list('column_name', flat=True)
            )
            discovered_columns = set()
            
            for column_data in columns_data:
                column_name = column_data['name']
                discovered_columns.add(column_name)
                
                # Get or create the column
                column, created = SourceColumn.objects.get_or_create(
                    table=table,
                    column_name=column_name,
                    defaults={
                        'column_position': column_data['position'],
                        'data_type': column_data['type_name'],
                        'physical_data_type': column_data.get('type_text', column_data['type_name']),
                        'is_nullable': column_data.get('nullable', True),
                        'is_primary_key': False,  # Would need additional logic to detect
                        'is_foreign_key': False,  # Would need additional logic to detect
                        'null_count': column_data.get('null_count', 0),
                        'distinct_count': column_data.get('distinct_count', 0),
                        'min_value': column_data.get('min_value'),
                        'max_value': column_data.get('max_value'),
                        'avg_length': column_data.get('avg_length'),
                        'column_comment': column_data.get('comment', ''),
                        'sample_values': column_data.get('sample_values', [])
                    }
                )
                
                if created:
                    stats['columns_created'] += 1
                else:
                    # Update existing column
                    column.column_position = column_data['position']
                    column.data_type = column_data['type_name']
                    column.physical_data_type = column_data.get('type_text', column_data['type_name'])
                    column.is_nullable = column_data.get('nullable', True)
                    column.null_count = column_data.get('null_count', column.null_count)
                    column.distinct_count = column_data.get('distinct_count', column.distinct_count)
                    column.min_value = column_data.get('min_value', column.min_value)
                    column.max_value = column_data.get('max_value', column.max_value)
                    column.avg_length = column_data.get('avg_length', column.avg_length)
                    column.column_comment = column_data.get('comment', column.column_comment)
                    column.sample_values = column_data.get('sample_values', column.sample_values)
                    column.last_updated = timezone.now()
                    column.save()
                    stats['columns_updated'] += 1
            
            # Mark removed columns as inactive (don't delete to preserve mappings)
            removed_columns = existing_columns - discovered_columns
            if removed_columns:
                SourceColumn.objects.filter(
                    table=table,
                    column_name__in=removed_columns
                ).update(last_updated=timezone.now())
                logger.info(f"Found {len(removed_columns)} removed columns in {table.full_table_name}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to sync columns for table {table.full_table_name}: {e}")
            raise
    
    def refresh_table_statistics(self, table: SourceTable) -> bool:
        """
        Refresh statistics for a specific table.
        """
        try:
            # Get updated table info
            table_info = self.databricks.get_table_info(
                table.catalog_name, 
                table.schema_name, 
                table.table_name
            )
            
            # Update table statistics
            table.row_count = table_info.get('row_count', table.row_count)
            table.size_bytes = table_info.get('size_bytes', table.size_bytes)
            table.last_analyzed = timezone.now()
            table.analysis_status = 'completed'
            table.save()
            
            # Refresh column statistics
            for column in table.columns.all():
                try:
                    column_stats = self.databricks.get_column_statistics(
                        table.catalog_name,
                        table.schema_name,
                        table.table_name,
                        column.column_name,
                        column.data_type
                    )
                    
                    # Update column statistics
                    column.null_count = column_stats.get('null_count', column.null_count)
                    column.distinct_count = column_stats.get('distinct_count', column.distinct_count)
                    column.min_value = column_stats.get('min_value', column.min_value)
                    column.max_value = column_stats.get('max_value', column.max_value)
                    column.avg_length = column_stats.get('avg_length', column.avg_length)
                    column.sample_values = column_stats.get('sample_values', column.sample_values)
                    column.last_updated = timezone.now()
                    column.save()
                    
                except Exception as e:
                    logger.warning(f"Failed to refresh stats for column {column.column_name}: {e}")
            
            logger.info(f"Refreshed statistics for table {table.full_table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh statistics for table {table.full_table_name}: {e}")
            table.analysis_status = 'failed'
            table.save()
            return False
    
    def search_and_sync_tables(self, user: User, search_term: str, 
                              catalogs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search for tables and sync them to the database.
        """
        try:
            # Search for tables in Databricks
            matching_tables = self.databricks.search_tables(search_term, catalogs)
            
            stats = {
                'tables_found': len(matching_tables),
                'tables_synced': 0,
                'tables_created': 0,
                'tables_updated': 0,
                'columns_created': 0,
                'columns_updated': 0,
                'errors': []
            }
            
            # Sync each found table
            for table_data in matching_tables:
                try:
                    table_stats = self.sync_table(user, table_data)
                    
                    stats['tables_synced'] += 1
                    if table_stats['created']:
                        stats['tables_created'] += 1
                    else:
                        stats['tables_updated'] += 1
                    
                    stats['columns_created'] += table_stats['columns_created']
                    stats['columns_updated'] += table_stats['columns_updated']
                    
                except Exception as e:
                    error_msg = f"Failed to sync table {table_data.get('full_name', 'unknown')}: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
            
            return stats
            
        except Exception as e:
            logger.error(f"Search and sync failed: {e}")
            return {
                'tables_found': 0,
                'tables_synced': 0,
                'tables_created': 0,
                'tables_updated': 0,
                'columns_created': 0,
                'columns_updated': 0,
                'errors': [f"Search and sync failed: {e}"]
            }


# Global service instance
discovery_service = DiscoveryService()
