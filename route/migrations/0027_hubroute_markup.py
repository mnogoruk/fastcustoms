# Generated by Django 3.2.3 on 2021-09-02 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0026_storge_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='hubroute',
            name='markup',
            field=models.FloatField(default=1),
        ),
    ]