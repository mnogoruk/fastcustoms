# Generated by Django 3.2.3 on 2021-06-30 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0016_auto_20210630_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routeinpath',
            name='path',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='routes', to='route.path'),
        ),
    ]