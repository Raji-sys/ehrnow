# Generated by Django 5.0.1 on 2024-11-17 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pharm', '0003_remove_purchase_drug_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='drug',
            old_name='generic_name',
            new_name='name',
        ),
    ]
