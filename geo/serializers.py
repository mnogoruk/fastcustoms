from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer
from geo.models import City, Zone, Country, State, Location
from geo.indexes import CityIndex

class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name', 'slug', 'code']

class CityIndexSerializer(HaystackSerializer):
    class Meta:
        index_classes = [CityIndex]
        fields = ['id', 'name', 'slug', 'state', 'location']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'slug', 'iso2', 'iso3', 'phone_code', 'flag_url', 'zone']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'slug', 'code', 'country']


class CitySerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'state', 'location']
