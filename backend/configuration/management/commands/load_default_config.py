"""
Management command to load default configuration settings.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from configuration.models import Configuration, get_default_configuration

User = get_user_model()


class Command(BaseCommand):
    help = 'Load default configuration settings into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing configuration settings',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Email of user to attribute changes to',
        )

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        user_email = options.get('user')
        
        # Get user for attribution
        user = None
        if user_email:
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'User with email {user_email} not found. Using system user.')
                )
        
        default_config = get_default_configuration()
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for section, settings in default_config.items():
            for key, value in settings.items():
                config, created = Configuration.objects.get_or_create(
                    section=section,
                    key=key,
                    defaults={
                        'value': value,
                        'updated_by': user,
                        'description': f'Default {section} configuration for {key}'
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created: {section}.{key}')
                    )
                elif overwrite:
                    config.value = value
                    config.updated_by = user
                    config.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated: {section}.{key}')
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.NOTICE(f'Skipped: {section}.{key} (already exists)')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nConfiguration loading completed:\n'
                f'  Created: {created_count}\n'
                f'  Updated: {updated_count}\n'
                f'  Skipped: {skipped_count}'
            )
        )
