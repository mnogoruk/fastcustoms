# Generated by Django 3.2.3 on 2021-06-26 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0004_auto_20210626_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceranked',
            name='currency',
            field=models.CharField(default='EUR', max_length=12),
        ),
    ]