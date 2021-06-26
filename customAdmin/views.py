from django.db.models import Count, F
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from customAdmin.serializers import HubRouteCreateUpdateAdminSerializer, ZoneRatesCreateUpdateAdminSerializer
from geo.models import Zone
from geo.serializers import ZoneSerializer
from route.models import HubRoute
from utils.views.mixins import FullnessMixin
from route.serializers import HubRouteShortSerializer


class RouteView(ModelViewSet, FullnessMixin):
    serializer_class = HubRouteCreateUpdateAdminSerializer
    queryset = HubRoute.objects.all()

    def get_queryset(self):
        fullness = self.fullness()
        if fullness == self.FullnessMode.FULL:
            return super().get_queryset().select_related('source', 'destination', 'timetable')
        if fullness == self.FullnessMode.SHORT:
            return super().get_queryset().select_related('source', 'destination')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HubRouteCreateUpdateAdminSerializer
        fullness = self.fullness()
        if fullness == self.FullnessMode.FULL:
            return HubRouteCreateUpdateAdminSerializer
        else:
            return HubRouteShortSerializer


class ZoneRateView(ModelViewSet):
    serializer_class = ZoneRatesCreateUpdateAdminSerializer
    queryset = Zone.objects.all()

    @action(detail=False, methods=['get'], name='Zone summary', url_path='summary', url_name='zone-summary')
    def zone_summary(self, request):
        res = []
        zones = Zone.objects.annotate(
            country_count=Count('country', distinct=True),
            states_count=Count('country__state', distinct=True),
            city_count=Count('country__state__city', distinct=True)
        )
        for zone in zones.all():
            zone_dict = {
                'zone': ZoneSerializer(instance=zone).data,
                'country_count': zone.country_count,
                'state_count': zone.states_count,
                'city_count': zone.city_count
            }
            res.append(zone_dict)
        return Response(data=res)
