from django.db import transaction
from rest_framework.serializers import ValidationError, ModelSerializer

from geo.models import City, Zone
from goods.models import Good
from order.models import OrderAgent, Special, Order
from order.serializers import OrderSerializer
from pricing.models import RouteRate, ZoneRate, ServiceAdditional, ServiceRanked
from pricing.serializers import ZoneRateSerializer, ServiceRankedSerializer, ServiceAdditionalSerializer, \
    RouteRateSerializer
from route.models import HubRoute, RouteTimeTable, Path
from route.serializers import HubRouteSerializer, RouteTimeTableSerializer, PathSerializer, PathRouteCreatableSerializer


class HubRouteAdminSerializer(HubRouteSerializer):
    additional_services = ServiceAdditionalSerializer(many=True, required=False)
    ranked_services = ServiceRankedSerializer(many=True, required=False)
    rates = RouteRateSerializer(many=True)
    timetable = RouteTimeTableSerializer(required=False)

    def validate_source(self, source):
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

    def validate_additional_services(self, services):
        if len(services) > 20:
            raise ValidationError("Limit of rates exceeded. Maximum is 20.")
        return services

    def validate_ranked_services(self, services):
        if len(services) > 20:
            raise ValidationError("Limit of rates exceeded. Maximum is 20.")
        return services

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
        rates = validated_data.pop('rates', [])
        timetable = validated_data.pop('timetable', None)
        additional_services = validated_data.pop('additional_services', [])
        ranked_services = validated_data.pop('ranked_services', [])

        with transaction.atomic():
            source = validated_data.pop('source')
            destination = validated_data.pop('destination')

            if timetable:
                timetable = RouteTimeTable.objects.create(**timetable)

            route = HubRoute.objects.create(
                source=source, destination=destination, timetable=timetable, **validated_data
            )

            for rate in rates:
                RouteRate.objects.create(**rate, route=route)

            for service in additional_services:
                ServiceAdditional.objects.create(**service, route=route)

            for service in ranked_services:
                ServiceRanked.objects.create(**service, route=route)

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
            route.rates.all().delete()
            for rate in rates:
                RouteRate.objects.create(**rate, route=route)
        if 'timetable' in validated_data:
            route.timetable.delete()
            timetable = RouteTimeTable.objects.create(**validated_data.pop('timetable'))
            route.timetable = timetable
        if 'additional_services' in validated_data:
            route.additional_services.all().delete()
            for service in validated_data.pop('additional_services'):
                ServiceAdditional.objects.create(**service, route=route)
        if 'ranked_services' in validated_data:
            route.ranked_services.all().delete()
            for service in validated_data.pop('ranked_services'):
                ServiceRanked.objects.create(**service, route=route)

        return super(HubRouteAdminSerializer, self).update(route, validated_data)

    class Meta:
        model = HubRoute
        exclude = ['created_at']


class ZoneRatesAdminSerializer(ModelSerializer):
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
        zone = super(ZoneRatesAdminSerializer, self).create(validated_data)
        for rate in rates:
            ZoneRate.objects.create(**rate, zone=zone)
        return zone

    def update(self, zone: Zone, validated_data):
        rates = validated_data.pop('rates')
        zone = super(ZoneRatesAdminSerializer, self).update(zone, validated_data)
        zone.rates.all().delete()
        for rate in rates:
            ZoneRate.objects.create(**rate, zone=zone)
        return zone

    class Meta:
        model = Zone
        fields = '__all__'


class PathCreatableSerializer(PathSerializer):
    routes = PathRouteCreatableSerializer(many=True)


class OrderAdminSerializer(OrderSerializer):
    path = PathCreatableSerializer()

    def create(self, validated_data):
        agent = OrderAgent.objects.create(**validated_data.pop('agent'))
        path = Path.creatable.create(**validated_data.pop('path'))
        good = Good.creatable.create(**validated_data.pop('good'))
        if 'special' in validated_data:
            special = Special.objects.create(**validated_data.pop('special'))
        else:
            special = Special.objects.create()
        return Order.objects.create(agent=agent, path=path, good=good, special=special)
