from django.db import transaction
from rest_framework.serializers import ValidationError

from geo.models import City
from pricing.models import RouteRate
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
        print(timetable)
        return timetable

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
        fields = '__all__'

class ZoneRateCreateUpdateAdminSerializer(ZoneRateSerializer):
    pass