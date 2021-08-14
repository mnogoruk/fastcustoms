import string
from random import choice

from django.db import transaction
from rest_framework.serializers import ValidationError, ModelSerializer
from rest_framework import serializers
from geo.models import City, Zone
from geo.serializers import ZoneShortSerializer
from order.serializers import OrderSerializer
from pricing.models import RouteRate, ZoneRate, ServiceAdditional, ServiceRanked, ZonePricingInfo
from pricing.serializers import ZoneRateSerializer, ServiceRankedSerializer, ServiceAdditionalSerializer, \
    RouteRateSerializer
from route.models import HubRoute, RouteTimeTable
from route.serializers import HubRouteSerializer, RouteTimeTableSerializer
from utils.enums import RouteType, PlaceType
from utils.functions import place_type_related_to_route_type


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

        r_type = validated_data.get('type')
        p_type_s = place_type_related_to_route_type(r_type, 's')
        p_type_d = place_type_related_to_route_type(r_type, 'd')

        with transaction.atomic():
            source = validated_data.pop('source')
            source.add_type(p_type_s)
            source.save()

            destination = validated_data.pop('destination')
            destination.add_type(p_type_d)
            destination.save()

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

        if route.type != validated_data.get('type', RouteType.default().value):

            old_r_type = route.type
            old_p_type_s = place_type_related_to_route_type(old_r_type, 's')
            old_p_type_d = place_type_related_to_route_type(old_r_type, 'd')

            new_r_type = validated_data.get('type', RouteType.default().value)
            new_p_type_s = place_type_related_to_route_type(new_r_type, 's')
            new_p_type_d = place_type_related_to_route_type(new_r_type, 'd')

            route.source.add_type(new_p_type_s)
            route.destination.add_type(new_p_type_d)

            if old_p_type_s != PlaceType.CITY.value:
                src_count = HubRoute.objects.src_count_by_type(source=route.source, r_type=old_r_type)
                if src_count <= 1:
                    route.source.exclude_type(old_p_type_s)

            if old_p_type_d != PlaceType.CITY.value:
                dst_count = HubRoute.objects.dst_count_by_type(dest=route.destination, r_type=old_r_type)
                if dst_count <= 1:
                    route.destination.exclude_type(old_p_type_d)

            route.source.save()
            route.destination.save()

        return super(HubRouteAdminSerializer, self).update(route, validated_data)

    class Meta:
        model = HubRoute
        exclude = ['created_at']


class ZoneRatesAdminSerializer(ModelSerializer):
    rates = ZoneRateSerializer(many=True)
    minimal_price = serializers.DecimalField(max_digits=20, decimal_places=2)

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
        minimal_price = validated_data.pop('minimal_price')
        z = ZonePricingInfo.objects.create(zone=zone, minimal_price=minimal_price)
        for rate in rates:
            ZoneRate.objects.create(**rate, zone=zone)
        zone.minimal_price = minimal_price
        return zone

    def update(self, zone: Zone, validated_data):
        rates = validated_data.pop('rates')
        minimal_price = validated_data.pop('minimal_price')

        zone = super(ZoneRatesAdminSerializer, self).update(zone, validated_data)
        zone.pricing_info.minimal_price = minimal_price
        zone.pricing_info.save()
        zone.rates.all().delete()
        for rate in rates:
            ZoneRate.objects.create(**rate, zone=zone)
        return zone

    class Meta:
        model = Zone
        fields = '__all__'


class OrderAdminSerializer(OrderSerializer):
    pass


class ZoneCreateSerializer(ZoneShortSerializer):
    def create(self, validated_data):
        name = validated_data['name']
        slug = name + ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(6))
        validated_data['slug'] = slug
        zone = super(ZoneCreateSerializer, self).create(validated_data)
        ZonePricingInfo.objects.create(zone=zone)
        return zone
