# Generated by Django 5.0.1 on 2024-12-08 16:55

import django.db.models.deletion
import django_quill.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ehr', '0020_alter_wallettransaction_amount'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='photo',
        ),
        migrations.AlterField(
            model_name='paypoint',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('CASH', 'CASH'), ('WALLET', 'WALLET'), ('CREDIT', 'CREDIT')], default='CASH', max_length=10, null=True),
        ),
        migrations.CreateModel(
            name='WardShiftNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', django_quill.fields.QuillField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('nurse', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ward_shift_notes', to='ehr.patientdata')),
            ],
            options={
                'verbose_name_plural': 'ward shift summary notes',
            },
        ),
        migrations.DeleteModel(
            name='WardShiftSUmmaryNote',
        ),
    ]
