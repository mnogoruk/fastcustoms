from rest_framework import serializers
from typing import List

from geo.models import City, Zone, Country, State, Location


class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class WithAliasSerializer(serializers.ModelSerializer):
    allowed_alias: List[str] = ['ru', 'en']
    alias_prefix: str = 'alias_'

    @classmethod
    def alias_fields(cls):
        return [cls.alias_prefix + al for al in cls.allowed_alias]

    def __init__(self, *args, **kwargs):

        alias = kwargs.pop('alias', [])

        super(WithAliasSerializer, self).__init__(*args, **kwargs)

        if alias is not None:
            if not isinstance(alias, list):
                raise ValueError("alias must be  List[str] instance")
            current = set(alias)
            existing = set(self.allowed_alias)
            for al in (existing - current):
                self.fields.pop(self.alias_prefix + al)


class ZoneShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name']


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name', 'slug', 'code']


class CountrySerializer(WithAliasSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'slug', 'iso2', 'iso3', 'phone_code', 'flag_url', 'alias_ru', 'alias_en']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'slug', 'code', 'country', 'zone']


class CitySerializer(WithAliasSerializer):
    location = LocationSerializer()

    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'state', 'location', 'alias_ru', 'alias_en']


class CityShortSerializer(WithAliasSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'alias_ru', 'alias_en']
