# Generated by Django 3.2.3 on 2021-06-30 12:47

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0005_alter_box_type'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='good',
            managers=[
                ('creatable', django.db.models.manager.Manager()),
            ],
        ),
    ]
