from rest_framework import serializers
from geo.models import City, Zone, Country, State, Location

class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name', 'slug', 'code']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'slug', 'iso2', 'iso3', 'phone_code', 'flag_url']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'slug', 'code', 'country', 'zone']


class CitySerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'state', 'location', 'types']

class CityShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']