from rest_framework import serializers
from pricing.models import RouteRate, ZoneRate, ServiceAdditional, ServiceRanked, ContainerRate


class RouteRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteRate
        exclude = ['id', 'route', 'created_at']


class ZoneRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoneRate
        exclude = ['id', 'zone', 'created_at']


class ServiceAdditionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAdditional
        exclude = ['id', 'route', 'created_at']


class ServiceRankedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRanked
        exclude = ['id', 'route', 'created_at']


class ContainerRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerRate
        exclude = ['id', 'route']
