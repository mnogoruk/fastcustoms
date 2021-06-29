from rest_framework import serializers

from geo.serializers import CitySerializer, CityShortSerializer
from goods.models import Box, Container, Good
from goods.serializers import GoodSerializer
from order.models import Special
from utils.calculation import ldm_from_size

from utils.enums import RouteType
from utils.serializers.fileds import PureLookUpFiled
from route.models import HubRoute, RouteTimeTable


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


class PathConclusionSerializer(serializers.Serializer):
    source = CitySerializer()
    destination = CitySerializer()

    paths = PathSerializer(many=True)


class SpecialSerializer(serializers.ModelSerializer):
    departure_date = serializers.DateField(required=False)

    class Meta:
        model = Special
        exclude = ['id']


class PathToCalculateSerializer(serializers.Serializer):
    source = PureLookUpFiled(CitySerializer(), lookup_fields=['id'])
    destination = PureLookUpFiled(CitySerializer(), lookup_fields=['id'])

    good = GoodSerializer(required=True)
    special = SpecialSerializer(required=False)

