# Generated by Django 3.2.3 on 2021-06-19 22:21

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0013_alter_hubroute_timetable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routetimetable',
            name='weekdays',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.BooleanField(), default=list, size=7),
        ),
    ]
