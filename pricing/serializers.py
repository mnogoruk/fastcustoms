from rest_framework import serializers

from geo.models import Zone
from pricing.models import RouteRate, ZoneRate


class RouteRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteRate
        exclude = ['route', 'created_at']


class ZoneRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ZoneRate
        exclude = ['zone', 'created_at']

