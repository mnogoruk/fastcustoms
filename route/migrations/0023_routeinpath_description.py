# Generated by Django 3.2.3 on 2021-08-22 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0022_auto_20210821_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='routeinpath',
            name='description',
            field=models.TextField(blank=True, default='', max_length=1000),
        ),
    ]
