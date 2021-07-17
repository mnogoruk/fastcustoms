from django.db import models, transaction
from dataclasses import dataclass
from django.contrib.postgres.fields import ArrayField

from utils.enums import PlaceType


@dataclass
class Location:
    latitude: float
    longitude: float

def default_type():
    return [PlaceType.default().value]


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

    types = ArrayField(
        models.CharField(max_length=20, choices=PlaceType.choices()),
        size=6,
        default=default_type)

    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='cities')

    def add_type(self, place_type: PlaceType):
        if place_type.value not in self.types:
            self.types.append(place_type.value)

    def exclude_type(self, place_type: PlaceType):
        if place_type.value in self.types:
            self.types.remove(place_type.value)

    @property
    def location(self):
        return Location(latitude=self.latitude, longitude=self.longitude)

    def __str__(self):
        return f"{self.name}"
