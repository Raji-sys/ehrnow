# In one of your apps, create the following file structure:
# your_app/management/commands/create_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Creates standard groups with predefined permissions'

    def handle(self, *args, **kwargs):
        # List of groups to create
        group_names = [
            'doctor', 'nurse', 'revenue', 'record','pharmacist', 'radiologist', 'physiotherapist', 'auditor','STORE','ACCOUNTING', 
        ]

        # Create groups
        for group_name in group_names:
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            else:
                self.stdout.write(self.style.NOTICE(f'Group already exists: {group_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully created all groups'))
