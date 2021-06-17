# Generated by Django 3.2.3 on 2021-05-29 21:05

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0009_auto_20210529_2345'),
    ]

    operations = [
        migrations.AddField(
            model_name='routetimetable',
            name='preparation_period',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='routetimetable',
            name='weekdays',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=[0, 0, 0, 0, 0, 0, 0], size=7),
        ),
    ]