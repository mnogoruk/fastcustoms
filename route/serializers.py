from rest_framework import serializers

from geo.models import City
from geo.serializers import CitySerializer, CityShortSerializer
from goods.serializers import GoodSerializer
from order.models import Special

from utils.enums import RouteType, PlaceType
from utils.serializers.fileds import PureLookUpFiled
from route.models import HubRoute, RouteTimeTable, RouteInPath


class RouteTimeTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteTimeTable
        fields = ['weekdays', 'preparation_period']


class PathRouteCreatableSerializer(serializers.ModelSerializer):
    source = PureLookUpFiled(CitySerializer(), lookup_fields=['id', 'slug'])
    destination = PureLookUpFiled(CitySerializer(), lookup_fields=['id', 'slug'])

    distance = serializers.FloatField()  # km
    duration = serializers.FloatField()  # days
    is_hub = serializers.BooleanField()
    type = serializers.ChoiceField(RouteType.choices())

    def validate_source(self, source):
        return City.objects.get(id=source['id'])

    def validate_destination(self, destination):
        return City.objects.get(id=destination['id'])

    class Meta:
        model = RouteInPath
        exclude = ['id']


class PathRouteReadSerializer(serializers.Serializer):
    source = CitySerializer(read_only=True)
    destination = CitySerializer(read_only=True)
    description = serializers.CharField(max_length=1000, default='')
    distance = serializers.FloatField(read_only=True)  # km
    duration = serializers.FloatField(read_only=True)  # days
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
        fields = ['id', 'source', 'destination', 'type', 'title', 'active', 'rates_valid_to']


class DurationSerializer(serializers.Serializer):
    min = serializers.FloatField()  # days
    max = serializers.FloatField()  # days


class PathSerializer(serializers.Serializer):
    total_distance = serializers.FloatField()  # km
    total_duration = DurationSerializer()  # pair in days
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
    source_type = serializers.ChoiceField(choices=PlaceType.choices(), default=PlaceType.CITY.value)
    destination_type = serializers.ChoiceField(choices=PlaceType.choices(), default=PlaceType.CITY.value)
