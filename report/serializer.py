import serializer
from rest_framework import serializers

from goods.serializers import GoodSerializer
from route.serializers import PathRouteCreatableSerializer, PathSerializer, DurationSerializer


class ReportPathSerializer(serializers.Serializer):
    total_distance = serializers.FloatField()  # km
    total_duration = DurationSerializer()  # pair in days
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2)

    routes = PathRouteCreatableSerializer(many=True)


class ReportInputSerializer(serializers.Serializer):
    path = ReportPathSerializer()
    customs = serializers.BooleanField(default=False)
    good = GoodSerializer()
