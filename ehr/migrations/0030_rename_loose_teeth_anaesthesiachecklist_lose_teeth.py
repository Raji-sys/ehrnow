# Generated by Django 5.0.1 on 2024-12-25 23:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ehr', '0029_remove_anaesthisiachecklist_concurrent_medical_illness_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='anaesthesiachecklist',
            old_name='loose_teeth',
            new_name='lose_teeth',
        ),
    ]
