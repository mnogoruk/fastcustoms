# Generated by Django 3.2.3 on 2021-07-17 14:06

import django.contrib.postgres.fields
from django.db import migrations, models
import geo.models


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0008_auto_20210708_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='types',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('CITY', 'CITY'), ('AIRPORT', 'AIRPORT'), ('RAILWAY_STATION', 'RAILWAY_STATION'), ('SEAPORT', 'SEAPORT')], max_length=20), default=geo.models.default_type, size=6),
        ),
    ]
