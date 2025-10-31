"""
Databricks integration service for the mapping application.

This service provides functionality to:
- Connect to Databricks SQL warehouses
- Discover tables and columns from catalogs
- Analyze table structures and statistics
- Execute queries for data profiling
- Integrate with Unity Catalog for metadata
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import TableInfo, ColumnInfo
import databricks.sql as sql
import pandas as pd

logger = logging.getLogger(__name__)


class DatabricksConnectionError(Exception):
    """Custom exception for Databricks connection issues."""
    pass


class DatabricksService:
    """
    Service class for interacting with Databricks.
    """
    
    def __init__(self):
        self.workspace_client = None
        self.sql_connection = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Databricks clients."""
        try:
            # Initialize Workspace Client for Unity Catalog operations
            if settings.DATABRICKS_HOST and settings.DATABRICKS_TOKEN:
                self.workspace_client = WorkspaceClient(
                    host=settings.DATABRICKS_HOST,
                    token=settings.DATABRICKS_TOKEN
                )
                logger.info("Databricks Workspace Client initialized successfully")
            else:
                logger.warning("Databricks credentials not configured")
                
        except Exception as e:
            logger.error(f"Failed to initialize Databricks clients: {e}")
            raise DatabricksConnectionError(f"Failed to connect to Databricks: {e}")
    
    def get_sql_connection(self):
        """Get a SQL connection to Databricks."""
        try:
            if not all([settings.DATABRICKS_HOST, settings.DATABRICKS_TOKEN, settings.DATABRICKS_HTTP_PATH]):
                raise DatabricksConnectionError("Databricks SQL connection parameters not configured")
            
            connection = sql.connect(
                server_hostname=settings.DATABRICKS_HOST.replace('https://', ''),
                http_path=settings.DATABRICKS_HTTP_PATH,
                access_token=settings.DATABRICKS_TOKEN
            )
            
            logger.info("Databricks SQL connection established")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create SQL connection: {e}")
            raise DatabricksConnectionError(f"Failed to connect to Databricks SQL: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Databricks connection."""
        try:
            # Test workspace client
            workspace_status = False
            if self.workspace_client:
                try:
                    # Try to list catalogs as a connection test
                    list(self.workspace_client.catalogs.list())
                    workspace_status = True
                except Exception as e:
                    logger.warning(f"Workspace client test failed: {e}")
            
            # Test SQL connection
            sql_status = False
            try:
                with self.get_sql_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    sql_status = True
            except Exception as e:
                logger.warning(f"SQL connection test failed: {e}")
            
            return {
                'workspace_client': workspace_status,
                'sql_connection': sql_status,
                'overall_status': workspace_status and sql_status
            }
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                'workspace_client': False,
                'sql_connection': False,
                'overall_status': False,
                'error': str(e)
            }
    
    def discover_catalogs(self) -> List[Dict[str, Any]]:
        """Discover available catalogs."""
        try:
            if not self.workspace_client:
                raise DatabricksConnectionError("Workspace client not available")
            
            catalogs = []
            for catalog in self.workspace_client.catalogs.list():
                catalogs.append({
                    'name': catalog.name,
                    'comment': catalog.comment,
                    'owner': catalog.owner,
                    'created_at': catalog.created_at,
                    'updated_at': catalog.updated_at
                })
            
            logger.info(f"Discovered {len(catalogs)} catalogs")
            return catalogs
            
        except Exception as e:
            logger.error(f"Failed to discover catalogs: {e}")
            raise DatabricksConnectionError(f"Failed to discover catalogs: {e}")
    
    def discover_schemas(self, catalog_name: str) -> List[Dict[str, Any]]:
        """Discover schemas in a catalog."""
        try:
            if not self.workspace_client:
                raise DatabricksConnectionError("Workspace client not available")
            
            schemas = []
            for schema in self.workspace_client.schemas.list(catalog_name=catalog_name):
                schemas.append({
                    'name': schema.name,
                    'catalog_name': schema.catalog_name,
                    'comment': schema.comment,
                    'owner': schema.owner,
                    'created_at': schema.created_at,
                    'updated_at': schema.updated_at
                })
            
            logger.info(f"Discovered {len(schemas)} schemas in catalog {catalog_name}")
            return schemas
            
        except Exception as e:
            logger.error(f"Failed to discover schemas in {catalog_name}: {e}")
            raise DatabricksConnectionError(f"Failed to discover schemas: {e}")
    
    def discover_tables(self, catalog_name: str, schema_name: str) -> List[Dict[str, Any]]:
        """Discover tables in a schema."""
        try:
            if not self.workspace_client:
                raise DatabricksConnectionError("Workspace client not available")
            
            tables = []
            for table in self.workspace_client.tables.list(
                catalog_name=catalog_name,
                schema_name=schema_name
            ):
                # Get additional table information
                table_info = self.get_table_info(catalog_name, schema_name, table.name)
                
                tables.append({
                    'name': table.name,
                    'catalog_name': table.catalog_name,
                    'schema_name': table.schema_name,
                    'full_name': f"{table.catalog_name}.{table.schema_name}.{table.name}",
                    'table_type': table.table_type,
                    'data_source_format': table.data_source_format,
                    'storage_location': table.storage_location,
                    'owner': table.owner,
                    'comment': table.comment,
                    'created_at': table.created_at,
                    'updated_at': table.updated_at,
                    **table_info  # Add row count and size if available
                })
            
            logger.info(f"Discovered {len(tables)} tables in {catalog_name}.{schema_name}")
            return tables
            
        except Exception as e:
            logger.error(f"Failed to discover tables in {catalog_name}.{schema_name}: {e}")
            raise DatabricksConnectionError(f"Failed to discover tables: {e}")
    
    def get_table_info(self, catalog_name: str, schema_name: str, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table."""
        try:
            full_table_name = f"{catalog_name}.{schema_name}.{table_name}"
            
            # Try to get table statistics
            table_stats = {}
            try:
                with self.get_sql_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) as row_count FROM {full_table_name}")
                    result = cursor.fetchone()
                    if result:
                        table_stats['row_count'] = result[0]
                    
                    # Get table size (if available)
                    try:
                        cursor.execute(f"DESCRIBE DETAIL {full_table_name}")
                        detail_result = cursor.fetchone()
                        if detail_result and len(detail_result) > 5:
                            table_stats['size_bytes'] = detail_result[5] if detail_result[5] else 0
                    except Exception:
                        # DESCRIBE DETAIL might not be available for all table types
                        table_stats['size_bytes'] = 0
                        
            except Exception as e:
                logger.warning(f"Could not get table statistics for {full_table_name}: {e}")
                table_stats = {'row_count': 0, 'size_bytes': 0}
            
            return table_stats
            
        except Exception as e:
            logger.error(f"Failed to get table info for {catalog_name}.{schema_name}.{table_name}: {e}")
            return {'row_count': 0, 'size_bytes': 0}
    
    def discover_columns(self, catalog_name: str, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
        """Discover columns in a table."""
        try:
            if not self.workspace_client:
                raise DatabricksConnectionError("Workspace client not available")
            
            full_table_name = f"{catalog_name}.{schema_name}.{table_name}"
            
            # Get column information from Unity Catalog
            columns = []
            table_info = self.workspace_client.tables.get(
                full_name=full_table_name
            )
            
            if table_info.columns:
                for i, column in enumerate(table_info.columns):
                    column_data = {
                        'name': column.name,
                        'position': i + 1,
                        'type_name': column.type_name,
                        'type_text': column.type_text,
                        'nullable': column.nullable,
                        'comment': column.comment,
                        'partition_index': column.partition_index,
                    }
                    
                    # Get column statistics if available
                    column_stats = self.get_column_statistics(
                        catalog_name, schema_name, table_name, column.name, column.type_name
                    )
                    column_data.update(column_stats)
                    
                    columns.append(column_data)
            
            logger.info(f"Discovered {len(columns)} columns in {full_table_name}")
            return columns
            
        except Exception as e:
            logger.error(f"Failed to discover columns in {catalog_name}.{schema_name}.{table_name}: {e}")
            raise DatabricksConnectionError(f"Failed to discover columns: {e}")
    
    def get_column_statistics(self, catalog_name: str, schema_name: str, table_name: str, 
                            column_name: str, column_type: str) -> Dict[str, Any]:
        """Get statistics for a specific column."""
        try:
            full_table_name = f"{catalog_name}.{schema_name}.{table_name}"
            stats = {}
            
            with self.get_sql_connection() as conn:
                cursor = conn.cursor()
                
                # Get basic statistics
                try:
                    # Null count
                    cursor.execute(f"""
                        SELECT COUNT(*) - COUNT(`{column_name}`) as null_count
                        FROM {full_table_name}
                    """)
                    result = cursor.fetchone()
                    stats['null_count'] = result[0] if result else 0
                    
                    # Distinct count (limit to avoid performance issues)
                    cursor.execute(f"""
                        SELECT COUNT(DISTINCT `{column_name}`) as distinct_count
                        FROM {full_table_name}
                        LIMIT 1000000
                    """)
                    result = cursor.fetchone()
                    stats['distinct_count'] = result[0] if result else 0
                    
                    # For string columns, get average length
                    if 'string' in column_type.lower() or 'varchar' in column_type.lower():
                        cursor.execute(f"""
                            SELECT AVG(LENGTH(`{column_name}`)) as avg_length
                            FROM {full_table_name}
                            WHERE `{column_name}` IS NOT NULL
                        """)
                        result = cursor.fetchone()
                        stats['avg_length'] = float(result[0]) if result and result[0] else 0.0
                    
                    # For numeric columns, get min/max
                    if any(t in column_type.lower() for t in ['int', 'bigint', 'decimal', 'double', 'float']):
                        cursor.execute(f"""
                            SELECT MIN(`{column_name}`), MAX(`{column_name}`)
                            FROM {full_table_name}
                            WHERE `{column_name}` IS NOT NULL
                        """)
                        result = cursor.fetchone()
                        if result:
                            stats['min_value'] = str(result[0]) if result[0] is not None else None
                            stats['max_value'] = str(result[1]) if result[1] is not None else None
                    
                    # Get sample values (limit to 5)
                    cursor.execute(f"""
                        SELECT DISTINCT `{column_name}`
                        FROM {full_table_name}
                        WHERE `{column_name}` IS NOT NULL
                        LIMIT 5
                    """)
                    sample_results = cursor.fetchall()
                    stats['sample_values'] = [str(row[0]) for row in sample_results] if sample_results else []
                    
                except Exception as e:
                    logger.warning(f"Could not get statistics for column {column_name}: {e}")
                    stats.update({
                        'null_count': 0,
                        'distinct_count': 0,
                        'sample_values': []
                    })
            
            return stats
            
        except Exception as e:
            logger.warning(f"Failed to get column statistics for {column_name}: {e}")
            return {
                'null_count': 0,
                'distinct_count': 0,
                'sample_values': []
            }
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame."""
        try:
            with self.get_sql_connection() as conn:
                df = pd.read_sql(query, conn)
                logger.info(f"Query executed successfully, returned {len(df)} rows")
                return df
                
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise DatabricksConnectionError(f"Query execution failed: {e}")
    
    def get_table_sample(self, catalog_name: str, schema_name: str, table_name: str, 
                        limit: int = 100) -> pd.DataFrame:
        """Get a sample of data from a table."""
        try:
            full_table_name = f"{catalog_name}.{schema_name}.{table_name}"
            query = f"SELECT * FROM {full_table_name} LIMIT {limit}"
            return self.execute_query(query)
            
        except Exception as e:
            logger.error(f"Failed to get table sample: {e}")
            raise DatabricksConnectionError(f"Failed to get table sample: {e}")
    
    def search_tables(self, search_term: str, catalogs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for tables by name or description."""
        try:
            if not self.workspace_client:
                raise DatabricksConnectionError("Workspace client not available")
            
            matching_tables = []
            search_term_lower = search_term.lower()
            
            # Get catalogs to search
            if not catalogs:
                catalogs = [cat['name'] for cat in self.discover_catalogs()]
            
            for catalog_name in catalogs:
                try:
                    schemas = self.discover_schemas(catalog_name)
                    for schema in schemas:
                        try:
                            tables = self.discover_tables(catalog_name, schema['name'])
                            for table in tables:
                                # Check if search term matches table name or comment
                                if (search_term_lower in table['name'].lower() or 
                                    (table.get('comment') and search_term_lower in table['comment'].lower())):
                                    matching_tables.append(table)
                        except Exception as e:
                            logger.warning(f"Could not search tables in {catalog_name}.{schema['name']}: {e}")
                            continue
                except Exception as e:
                    logger.warning(f"Could not search schemas in {catalog_name}: {e}")
                    continue
            
            logger.info(f"Found {len(matching_tables)} tables matching '{search_term}'")
            return matching_tables
            
        except Exception as e:
            logger.error(f"Table search failed: {e}")
            raise DatabricksConnectionError(f"Table search failed: {e}")


# Global service instance
databricks_service = DatabricksService()
