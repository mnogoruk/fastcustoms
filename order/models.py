from django.db import models

# Create your models here.
from goods.models import Good
from route.models import Path


class OrderUnit(models.Model):
    company_name = models.CharField(max_length=250)
    index = models.CharField(max_length=50)
    address = models.CharField(max_length=500)
    contact_person = models.CharField(max_length=250)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=120)


class Special(models.Model):
    departure_date = models.DateField()

class Order(models.Model):
    shipper = models.OneToOneField(OrderUnit, on_delete=models.CASCADE, related_name='order_by_shipper')
    consignee = models.OneToOneField(OrderUnit, on_delete=models.CASCADE, related_name='order_by_consignee')

    path = models.OneToOneField(Path, on_delete=models.CASCADE, related_name='order')
    good = models.OneToOneField(Good, on_delete=models.CASCADE, related_name='order')
    special = models.OneToOneField(Special, on_delete=models.CASCADE, related_name='order')
