from rest_framework import serializers

from geo.models import Zone
from pricing.models import RouteRate, ZoneRate, ServiceAdditional, ServiceRanked


class RouteRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteRate
        exclude = ['route', 'created_at']


class ZoneRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ZoneRate
        exclude = ['zone', 'created_at']

class ServiceAdditionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceAdditional
        exclude = ['route', 'created_at']

class ServiceRankedSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceRanked
        exclude = ['route', 'created_at']
