# Generated by Django 3.2.3 on 2021-09-13 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0027_hubroute_markup'),
    ]

    operations = [
        migrations.AddField(
            model_name='path',
            name='cheapest',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='path',
            name='fastest',
            field=models.BooleanField(default=False),
        ),
    ]
