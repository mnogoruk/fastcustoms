# Generated by Django 3.2.3 on 2021-07-30 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0019_auto_20210722_2316'),
    ]

    operations = [
        migrations.AddField(
            model_name='hubroute',
            name='minimal_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
    ]