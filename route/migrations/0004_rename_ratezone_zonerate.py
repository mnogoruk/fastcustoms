# Generated by Django 3.2.2 on 2021-05-20 19:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0006_auto_20210512_1932'),
        ('route', '0003_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RateZone',
            new_name='ZoneRate',
        ),
    ]
