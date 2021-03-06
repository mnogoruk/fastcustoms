# Generated by Django 3.2.3 on 2021-07-15 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_order_time_stamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderAgent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=250)),
                ('address', models.CharField(max_length=500)),
                ('contact_person', models.CharField(max_length=250)),
                ('phone', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=120)),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='consignee',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipper',
        ),
        migrations.DeleteModel(
            name='OrderUnit',
        ),
        migrations.AddField(
            model_name='order',
            name='agent',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order', to='order.orderagent'),
        ),
    ]
