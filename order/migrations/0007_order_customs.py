# Generated by Django 3.2.3 on 2021-07-24 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_alter_order_time_stamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='customs',
            field=models.BooleanField(default=False),
        ),
    ]