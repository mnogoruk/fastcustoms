# Generated by Django 3.2.3 on 2021-08-08 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0020_minimal_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hubroute',
            name='type',
            field=models.CharField(choices=[('TRUCK', 'TRUCK'), ('TRAIN', 'TRAIN'), ('AIR', 'AIR'), ('SEA', 'SEA')], default='TRUCK', max_length=20),
        ),
        migrations.AlterField(
            model_name='routeinpath',
            name='type',
            field=models.CharField(choices=[('TRUCK', 'TRUCK'), ('TRAIN', 'TRAIN'), ('AIR', 'AIR'), ('SEA', 'SEA')], default='TRUCK', max_length=20),
        ),
    ]
