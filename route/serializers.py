from django.db import transaction
from rest_framework import serializers

from geo.models import City, Zone
from geo.serializers import CitySerializer
from pricing.models import RouteRate
from pricing.serializers import RouteRateSerializer
from utils.enums import RouteType, Currency, RateType, RateUseType
from utils.serializers.fileds import PureLookUpFiled
from .models import HubRoute, Path


class PathRouteReadSerializer(serializers.Serializer):
    source = CitySerializer(read_only=True)
    destination = CitySerializer(read_only=True)

    distance = serializers.IntegerField(read_only=True)
    duration = serializers.IntegerField(read_only=True)
    is_hub = serializers.BooleanField(read_only=True)
    type = serializers.ChoiceField(RouteType.choices(), read_only=True)


class HubRouteCreateSerializer(serializers.ModelSerializer):
    source = PureLookUpFiled(CitySerializer(), lookup_fields=['id', 'slug'])
    destination = PureLookUpFiled(CitySerializer(), lookup_fields=['id', 'slug'])

    rates = RouteRateSerializer(many=True)

    def create(self, validated_data):
        source = City.objects.get(**validated_data.pop('source'))
        destination = City.objects.get(**validated_data.pop('destination'))

        rates = validated_data.pop('rates')
        with transaction.atomic():
            route = HubRoute.objects.create(source=source, destination=destination, **validated_data)

            for rate in rates:
                RouteRate.objects.create(**rate, route=route)

        return route

    class Meta:
        model = HubRoute
        fields = '__all__'


class DurationSerializer(serializers.Serializer):
    min = serializers.IntegerField()
    max = serializers.IntegerField()


class PathSerializer(serializers.Serializer):
    total_distance = serializers.IntegerField()
    total_duration = DurationSerializer()
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2)

    routes = PathRouteReadSerializer(many=True)

    def create(self, validated_data):
        print(validated_data)
        return Path.objects.create()


class PathConclusionSerializer(serializers.Serializer):
    source = CitySerializer()
    destination = CitySerializer()

    paths = PathSerializer(many=True)
