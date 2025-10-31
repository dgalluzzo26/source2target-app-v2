"""
Django management command to populate sample mapping data.

This command creates sample source tables, target schemas, and mappings
for testing and demonstration purposes.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mapping.models import (
    SourceTable, SourceColumn, TargetSchema, TargetField,
    FieldMapping, AIMapping, MappingTemplate, MappingSession
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample mapping data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing mapping data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing mapping data...')
            SourceTable.objects.all().delete()
            TargetSchema.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@gainwell.com',
            defaults={
                'username': 'admin',
                'full_name': 'System Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        # Create sample source tables
        self.stdout.write('Creating sample source tables...')
        
        # Customer table
        customer_table = SourceTable.objects.create(
            catalog_name='oztest_dev',
            schema_name='raw_data',
            table_name='customers',
            full_table_name='oztest_dev.raw_data.customers',
            table_type='TABLE',
            table_format='DELTA',
            owner='data_team@gainwell.com',
            source_owners='admin@gainwell.com,user@gainwell.com',
            row_count=150000,
            size_bytes=45000000,
            discovered_by=admin_user,
            analysis_status='completed'
        )

        # Customer columns
        customer_columns = [
            {'name': 'customer_id', 'type': 'BIGINT', 'pos': 1, 'pk': True, 'comment': 'Unique customer identifier'},
            {'name': 'first_name', 'type': 'STRING', 'pos': 2, 'comment': 'Customer first name'},
            {'name': 'last_name', 'type': 'STRING', 'pos': 3, 'comment': 'Customer last name'},
            {'name': 'email', 'type': 'STRING', 'pos': 4, 'comment': 'Customer email address'},
            {'name': 'phone', 'type': 'STRING', 'pos': 5, 'comment': 'Customer phone number'},
            {'name': 'date_of_birth', 'type': 'DATE', 'pos': 6, 'comment': 'Customer date of birth'},
            {'name': 'address_line1', 'type': 'STRING', 'pos': 7, 'comment': 'Primary address line'},
            {'name': 'address_line2', 'type': 'STRING', 'pos': 8, 'comment': 'Secondary address line'},
            {'name': 'city', 'type': 'STRING', 'pos': 9, 'comment': 'City name'},
            {'name': 'state', 'type': 'STRING', 'pos': 10, 'comment': 'State code'},
            {'name': 'zip_code', 'type': 'STRING', 'pos': 11, 'comment': 'ZIP/postal code'},
            {'name': 'created_at', 'type': 'TIMESTAMP', 'pos': 12, 'comment': 'Record creation timestamp'},
            {'name': 'updated_at', 'type': 'TIMESTAMP', 'pos': 13, 'comment': 'Record update timestamp'},
        ]

        for col_data in customer_columns:
            SourceColumn.objects.create(
                table=customer_table,
                column_name=col_data['name'],
                column_position=col_data['pos'],
                data_type=col_data['type'],
                physical_data_type=col_data['type'],
                is_nullable=not col_data.get('pk', False),
                is_primary_key=col_data.get('pk', False),
                column_comment=col_data['comment'],
                sample_values=['sample1', 'sample2', 'sample3'] if col_data['type'] == 'STRING' else []
            )

        # Orders table
        orders_table = SourceTable.objects.create(
            catalog_name='oztest_dev',
            schema_name='raw_data',
            table_name='orders',
            full_table_name='oztest_dev.raw_data.orders',
            table_type='TABLE',
            table_format='DELTA',
            owner='data_team@gainwell.com',
            source_owners='admin@gainwell.com,user@gainwell.com',
            row_count=500000,
            size_bytes=120000000,
            discovered_by=admin_user,
            analysis_status='completed'
        )

        # Order columns
        order_columns = [
            {'name': 'order_id', 'type': 'BIGINT', 'pos': 1, 'pk': True, 'comment': 'Unique order identifier'},
            {'name': 'customer_id', 'type': 'BIGINT', 'pos': 2, 'fk': True, 'comment': 'Reference to customer'},
            {'name': 'order_date', 'type': 'DATE', 'pos': 3, 'comment': 'Date order was placed'},
            {'name': 'order_status', 'type': 'STRING', 'pos': 4, 'comment': 'Current order status'},
            {'name': 'total_amount', 'type': 'DECIMAL(10,2)', 'pos': 5, 'comment': 'Total order amount'},
            {'name': 'tax_amount', 'type': 'DECIMAL(10,2)', 'pos': 6, 'comment': 'Tax amount'},
            {'name': 'shipping_amount', 'type': 'DECIMAL(10,2)', 'pos': 7, 'comment': 'Shipping cost'},
            {'name': 'payment_method', 'type': 'STRING', 'pos': 8, 'comment': 'Payment method used'},
            {'name': 'shipping_address', 'type': 'STRING', 'pos': 9, 'comment': 'Shipping address'},
            {'name': 'created_at', 'type': 'TIMESTAMP', 'pos': 10, 'comment': 'Record creation timestamp'},
            {'name': 'updated_at', 'type': 'TIMESTAMP', 'pos': 11, 'comment': 'Record update timestamp'},
        ]

        for col_data in order_columns:
            SourceColumn.objects.create(
                table=orders_table,
                column_name=col_data['name'],
                column_position=col_data['pos'],
                data_type=col_data['type'],
                physical_data_type=col_data['type'],
                is_nullable=not col_data.get('pk', False),
                is_primary_key=col_data.get('pk', False),
                is_foreign_key=col_data.get('fk', False),
                column_comment=col_data['comment'],
                sample_values=['sample1', 'sample2', 'sample3'] if col_data['type'] == 'STRING' else []
            )

        # Create target schema
        self.stdout.write('Creating target schema...')
        
        target_schema = TargetSchema.objects.create(
            schema_name='semantic_customer_360',
            display_name='Customer 360 Semantic Layer',
            description='Comprehensive customer view with unified data model',
            version='1.0',
            schema_type='semantic',
            created_by=admin_user
        )

        # Target fields
        target_fields = [
            {'name': 'customer_key', 'type': 'BIGINT', 'required': True, 'pk': True, 
             'desc': 'Surrogate key for customer dimension'},
            {'name': 'customer_natural_key', 'type': 'STRING', 'required': True,
             'desc': 'Natural business key for customer'},
            {'name': 'full_name', 'type': 'STRING', 'required': True,
             'desc': 'Complete customer name'},
            {'name': 'email_address', 'type': 'STRING', 'required': False,
             'desc': 'Primary email contact'},
            {'name': 'phone_number', 'type': 'STRING', 'required': False,
             'desc': 'Primary phone contact'},
            {'name': 'birth_date', 'type': 'DATE', 'required': False,
             'desc': 'Customer date of birth'},
            {'name': 'full_address', 'type': 'STRING', 'required': False,
             'desc': 'Complete formatted address'},
            {'name': 'city_name', 'type': 'STRING', 'required': False,
             'desc': 'City of residence'},
            {'name': 'state_code', 'type': 'STRING', 'required': False,
             'desc': 'State or province code'},
            {'name': 'postal_code', 'type': 'STRING', 'required': False,
             'desc': 'ZIP or postal code'},
            {'name': 'customer_since_date', 'type': 'DATE', 'required': True,
             'desc': 'Date customer first registered'},
            {'name': 'last_updated_date', 'type': 'TIMESTAMP', 'required': True,
             'desc': 'Last modification timestamp'},
        ]

        for field_data in target_fields:
            TargetField.objects.create(
                schema=target_schema,
                field_name=field_data['name'],
                field_path=field_data['name'],
                data_type=field_data['type'],
                is_required=field_data['required'],
                is_primary_key=field_data.get('pk', False),
                field_description=field_data['desc'],
                example_values=['example1', 'example2'] if field_data['type'] == 'STRING' else []
            )

        # Create some sample mappings
        self.stdout.write('Creating sample field mappings...')
        
        # Get source columns and target fields
        customer_id_col = SourceColumn.objects.get(table=customer_table, column_name='customer_id')
        customer_key_field = TargetField.objects.get(schema=target_schema, field_name='customer_natural_key')
        
        first_name_col = SourceColumn.objects.get(table=customer_table, column_name='first_name')
        last_name_col = SourceColumn.objects.get(table=customer_table, column_name='last_name')
        full_name_field = TargetField.objects.get(schema=target_schema, field_name='full_name')
        
        email_col = SourceColumn.objects.get(table=customer_table, column_name='email')
        email_field = TargetField.objects.get(schema=target_schema, field_name='email_address')

        # Direct mapping: customer_id -> customer_natural_key
        FieldMapping.objects.create(
            source_column=customer_id_col,
            target_field=customer_key_field,
            mapping_type='direct',
            confidence_score=0.95,
            is_validated=True,
            created_by=admin_user,
            validated_by=admin_user,
            status='approved'
        )

        # Transformed mapping: first_name + last_name -> full_name
        FieldMapping.objects.create(
            source_column=first_name_col,
            target_field=full_name_field,
            mapping_type='transformed',
            transformation_logic="CONCAT(first_name, ' ', last_name)",
            transformation_language='sql',
            confidence_score=0.90,
            is_validated=True,
            created_by=admin_user,
            validated_by=admin_user,
            status='approved'
        )

        # Direct mapping: email -> email_address
        FieldMapping.objects.create(
            source_column=email_col,
            target_field=email_field,
            mapping_type='direct',
            confidence_score=0.98,
            is_validated=True,
            created_by=admin_user,
            validated_by=admin_user,
            status='approved'
        )

        # Create some AI suggestions
        self.stdout.write('Creating AI mapping suggestions...')
        
        phone_col = SourceColumn.objects.get(table=customer_table, column_name='phone')
        phone_field = TargetField.objects.get(schema=target_schema, field_name='phone_number')
        
        AIMapping.objects.create(
            source_column=phone_col,
            target_field=phone_field,
            model_name='databricks-dbrx-instruct',
            model_version='2024-03',
            confidence_score=0.92,
            reasoning='Both fields represent customer phone contact information. High semantic similarity in field names and data types.',
            similarity_score=0.89,
            context_used={'field_name_similarity': 0.85, 'data_type_match': True, 'business_context': 'customer_contact'},
            status='pending'
        )

        # Create a mapping session
        self.stdout.write('Creating sample mapping session...')
        
        session = MappingSession.objects.create(
            user=admin_user,
            session_name='Customer Data Migration - Phase 1',
            target_schema=target_schema,
            notes='Initial mapping session for customer 360 semantic layer',
            tags=['customer', 'migration', 'phase1'],
            status='active'
        )
        session.source_tables.add(customer_table, orders_table)
        session.update_progress()

        # Create a mapping template
        self.stdout.write('Creating mapping template...')
        
        MappingTemplate.objects.create(
            name='Customer Data Standard Mapping',
            description='Standard mappings for customer data to semantic layer',
            source_schema_pattern='*.raw_data.customers',
            target_schema=target_schema,
            mapping_rules={
                'direct_mappings': [
                    {'source': 'customer_id', 'target': 'customer_natural_key'},
                    {'source': 'email', 'target': 'email_address'},
                    {'source': 'phone', 'target': 'phone_number'}
                ],
                'transformed_mappings': [
                    {
                        'sources': ['first_name', 'last_name'],
                        'target': 'full_name',
                        'logic': "CONCAT({first_name}, ' ', {last_name})"
                    }
                ]
            },
            transformation_templates={
                'name_concatenation': "CONCAT({first_name}, ' ', {last_name})",
                'address_formatting': "CONCAT({address_line1}, ', ', {city}, ', ', {state}, ' ', {zip_code})"
            },
            created_by=admin_user
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated sample data:\n'
                f'- {SourceTable.objects.count()} source tables\n'
                f'- {SourceColumn.objects.count()} source columns\n'
                f'- {TargetSchema.objects.count()} target schemas\n'
                f'- {TargetField.objects.count()} target fields\n'
                f'- {FieldMapping.objects.count()} field mappings\n'
                f'- {AIMapping.objects.count()} AI suggestions\n'
                f'- {MappingSession.objects.count()} mapping sessions\n'
                f'- {MappingTemplate.objects.count()} mapping templates'
            )
        )
