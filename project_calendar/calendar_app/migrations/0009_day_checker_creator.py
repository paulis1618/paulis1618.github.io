# Generated by Django 5.0.6 on 2025-02-11 17:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_app', '0008_day_checker_remove_emailsender_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='day_checker',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
