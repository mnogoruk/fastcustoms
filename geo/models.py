from django.db import models
from dataclasses import dataclass


@dataclass
class Location:
    latitude: float
    longitude: float


class Zone(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    code = models.CharField(max_length=5, null=True)

    def __str__(self):
        return f"{self.name}"


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


class State(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    code = models.CharField(max_length=50, null=True)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name}"


class City(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)

    @property
    def location(self):
        return Location(latitude=self.latitude, longitude=self.longitude)

    def __str__(self):
        return f"{self.name}"
