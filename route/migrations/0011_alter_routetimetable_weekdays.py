# Generated by Django 3.2.3 on 2021-05-29 21:06

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0010_auto_20210530_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routetimetable',
            name='weekdays',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=7),
        ),
    ]
