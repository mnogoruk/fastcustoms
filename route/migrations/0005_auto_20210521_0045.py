# Generated by Django 3.2.2 on 2021-05-20 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0004_rename_ratezone_zonerate'),
    ]

    operations = [
        migrations.AddField(
            model_name='path',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='path',
            name='total_distance',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='path',
            name='total_duration',
            field=models.IntegerField(default=0),
        ),
    ]
