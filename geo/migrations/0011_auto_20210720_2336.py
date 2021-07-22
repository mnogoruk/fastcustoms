# Generated by Django 3.2.3 on 2021-07-20 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0010_auto_20210720_2329'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='geo.country'),
        ),
        migrations.AlterField(
            model_name='country',
            name='capital',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='country_as_capital', to='geo.city'),
        ),
    ]
