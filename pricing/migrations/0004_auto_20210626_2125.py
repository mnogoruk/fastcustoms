# Generated by Django 3.2.3 on 2021-06-26 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0003_serviceadditional_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceranked',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='serviceranked',
            name='range_from',
        ),
        migrations.RemoveField(
            model_name='serviceranked',
            name='range_to',
        ),
        migrations.AddField(
            model_name='serviceranked',
            name='rank_type',
            field=models.CharField(choices=[('MASS', 'MASS'), ('SIZE', 'SIZE'), ('LDM', 'LDM')], default='MASS', max_length=20),
            preserve_default=False,
        ),
    ]
