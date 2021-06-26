from django.db import transaction
from rest_framework import serializers

from geo.models import City, Zone
from geo.serializers import CitySerializer, CityShortSerializer
from pricing.models import RouteRate
from pricing.serializers import RouteRateSerializer
from utils.enums import RouteType, Currency, RateType, RateUseType
from utils.serializers.fileds import PureLookUpFiled
from .models import HubRoute, Path, RouteTimeTable


class RouteTimeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteTimeTable
        fields = ['weekdays', 'preparation_period']


class PathRouteReadSerializer(serializers.Serializer):
    source = CitySerializer(read_only=True)
    destination = CitySerializer(read_only=True)

    distance = serializers.IntegerField(read_only=True)
    duration = serializers.IntegerField(read_only=True)
    is_hub = serializers.BooleanField(read_only=True)
    type = serializers.ChoiceField(RouteType.choices(), read_only=True)


class HubRouteSerializer(serializers.ModelSerializer):
    source = PureLookUpFiled(CitySerializer(), lookup_fields=['id', 'slug'])
    destination = PureLookUpFiled(CitySerializer(), lookup_fields=['id', 'slug'])

    class Meta:
        model = HubRoute
        exclude = ['created_at']


class HubRouteShortSerializer(serializers.ModelSerializer):
    source = CityShortSerializer()
    destination = CityShortSerializer()

    class Meta:
        model = HubRoute
        fields = ['id', 'source', 'destination', 'type']


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
