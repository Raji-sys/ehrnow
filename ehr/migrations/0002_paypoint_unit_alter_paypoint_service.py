# Generated by Django 5.0.1 on 2024-11-15 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ehr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paypoint',
            name='unit',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='paypoint',
            name='service',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
