from django.db import models, transaction
from dataclasses import dataclass


@dataclass
class Location:
    latitude: float
    longitude: float


class Country(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    iso2 = models.CharField(max_length=2, null=True)
    iso3 = models.CharField(max_length=3, null=True)
    phone_code = models.CharField(max_length=20, null=True)
    flag_url = models.URLField(null=True)

    capital = models.OneToOneField('City', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name}"


class Zone(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    code = models.CharField(max_length=5, null=True)

    def associate_with_country(self, country):
        """ Just add all country states to zone. """
        with transaction.atomic():
            for state in country.states.all():
                state.zone = self
                state.save()

    def __str__(self):
        return f"{self.name}"

class State(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    code = models.CharField(max_length=50, null=True)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='states')
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, related_name='states')

    def __str__(self):
        return f"{self.name}"


class City(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='cities')

    @property
    def location(self):
        return Location(latitude=self.latitude, longitude=self.longitude)

    def __str__(self):
        return f"{self.name}"
