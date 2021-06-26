from django.db import transaction
from rest_framework.serializers import ValidationError, ModelSerializer

from geo.models import City, Zone
from pricing.models import RouteRate, ZoneRate
from pricing.serializers import ZoneRateSerializer
from route.models import HubRoute, RouteTimeTable
from route.serializers import HubRouteSerializer


class HubRouteCreateUpdateAdminSerializer(HubRouteSerializer):

    def validate_source(self, source):
        print(source)
        try:
            source = City.objects.get(**source)
        except City.DoesNotExist:
            raise ValidationError("Source city does not exist.")

        return source

    def validate_destination(self, destination):
        try:
            destination = City.objects.get(**destination)
        except City.DoesNotExist:
            raise ValidationError("Destination city does not exist.")

        return destination

    def validate_timetable(self, timetable):
        weekdays = timetable['weekdays']
        if len(weekdays) != 7:
            raise ValidationError("'weekdays' must contains 7 items.")
        return timetable

    def validate_rates(self, rates):
        # TODO: validate intersections
        if len(rates) > 20:
            raise ValidationError("Limit of rates exceeded. Maximum is 20.")
        if len(rates) < 1:
            raise ValidationError("Limit of rates exceeded. Minimum is 1.")
        return rates

    def create(self, validated_data):
        rates = validated_data.pop('rates')
        timetable = validated_data.pop('timetable')

        with transaction.atomic():
            source = validated_data.pop('source')
            destination = validated_data.pop('destination')
            timetable = RouteTimeTable.objects.create(**timetable)

            route = HubRoute.objects.create(
                source=source, destination=destination, timetable=timetable, **validated_data
            )

            for rate in rates:
                RouteRate.objects.create(**rate, route=route)

        return route

    def update(self, route: HubRoute, validated_data: dict):
        if 'source' in validated_data:
            source = validated_data.pop('source')
            route.source = source
        if 'destination' in validated_data:
            destination = validated_data.pop('destination')
            route.destination = destination
        if 'rates' in validated_data:
            rates = validated_data.pop('rates')
            RouteRate.objects.filter(route=route).delete()
            for rate in rates:
                RouteRate.objects.create(**rate, route=route)
        if 'timetable' in validated_data:
            route.timetable.delete()
            timetable = RouteTimeTable.objects.create(**validated_data.pop('timetable'))
            route.timetable = timetable

        return super(HubRouteCreateUpdateAdminSerializer, self).update(route, validated_data)

    class Meta:
        model = HubRoute
        exclude = ['created_at']


class ZoneRatesCreateUpdateAdminSerializer(ModelSerializer):
    rates = ZoneRateSerializer(many=True)

    def validate_rates(self, rates):
        # TODO: validate intersections
        if len(rates) > 20:
            raise ValidationError("Limit of rates exceeded. Maximum is 20.")
        if len(rates) < 1:
            raise ValidationError("Limit of rates exceeded. Minimum is 1.")
        return rates

    def create(self, validated_data):
        rates = validated_data.pop('rates')
        zone = super(ZoneRatesCreateUpdateAdminSerializer, self).create(validated_data)
        for rate in rates:
            ZoneRate.objects.create(**rate, zone=zone)
        return zone

    def update(self, zone: Zone, validated_data):
        rates = validated_data.pop('rates')
        zone = super(ZoneRatesCreateUpdateAdminSerializer, self).update(zone, validated_data)
        zone.rates.all().delete()
        for rate in rates:
            ZoneRate.objects.create(**rate, zone=zone)
        return zone


    class Meta:
        model = Zone
        fields = '__all__'
