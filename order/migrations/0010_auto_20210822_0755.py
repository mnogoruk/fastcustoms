# Generated by Django 3.2.3 on 2021-08-22 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_auto_20210821_2220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderagent',
            name='comment',
            field=models.TextField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='orderagent',
            name='company_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='orderagent',
            name='email',
            field=models.EmailField(blank=True, max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='orderagent',
            name='phone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]