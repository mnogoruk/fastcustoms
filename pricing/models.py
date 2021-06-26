from django.db import models
from geo.models import Zone
from pricing.managers import RateManager
from route.models import HubRoute
from utils.db.models import AbstractCreate
from utils.enums import Currency, RateType


class AbstractRate(AbstractCreate):
    range_from = models.FloatField()
    range_to = models.FloatField()

    price_per_unit = models.DecimalField(max_digits=20, decimal_places=8)
    currency = models.CharField(max_length=12, default=Currency.EURO.value)

    type = models.CharField(choices=RateType.choices(), max_length=20)

    class Meta:
        abstract = True


class RouteRate(AbstractRate):
    route = models.ForeignKey(HubRoute, on_delete=models.CASCADE, related_name='rates')

    objects = RateManager()

    def __str__(self):
        return f"{self.route}: {self.range_from} - {self.range_to} ({self.price_per_unit})"


class ZoneRate(AbstractRate):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='rates')

    objects = RateManager()

    def __str__(self):
        return f"{self.zone}: {self.range_from} - {self.range_to} ({self.price_per_unit})"

class ServiceAdditional(AbstractCreate):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=12, default=Currency.EURO.value)
    route = models.ForeignKey(HubRoute, on_delete=models.CASCADE, related_name='additional_services')
    type = 'ADDITIONAL'

    def __str__(self):
        return f"{self.route}: {self.name}"

class ServiceRanked(AbstractRate):
    name = models.CharField(max_length=120)
    route = models.ForeignKey(HubRoute, on_delete=models.CASCADE, related_name='ranked_services')
    type = "RANKED"

    def __str__(self):
        return f"{self.route}: {self.name}"