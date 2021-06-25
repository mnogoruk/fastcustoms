from rest_framework import serializers

from geo.models import Zone
from pricing.models import RouteRate, ZoneRate


class RouteRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteRate
        exclude = ['route', 'created_at']


class ZoneRateSerializer(serializers.ModelSerializer):
    zone = serializers.PrimaryKeyRelatedField(queryset=Zone.objects.all())

    class Meta:
        model = ZoneRate
        exclude = ['created_at']
