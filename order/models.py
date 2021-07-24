from django.db import models

# Create your models here.
from goods.models import Good
from route.models import Path


class OrderAgent(models.Model):
    company_name = models.CharField(max_length=250)
    address = models.CharField(max_length=500)
    contact_person = models.CharField(max_length=250)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=120)


class Special(models.Model):
    departure_date = models.DateField(null=True)


class Order(models.Model):
    agent = models.OneToOneField(OrderAgent, on_delete=models.CASCADE, related_name='order', null=True, default=None)

    path = models.OneToOneField(Path, on_delete=models.CASCADE, related_name='order')
    good = models.OneToOneField(Good, on_delete=models.CASCADE, related_name='order')
    special = models.OneToOneField(Special, on_delete=models.CASCADE, related_name='order', null=True)
    time_stamp = models.DateTimeField(auto_created=True, auto_now_add=True)
    customs = models.BooleanField(default=False)
