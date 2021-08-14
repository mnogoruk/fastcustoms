from django.db.models import Count, F
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK

from common.models import Customs
from customAdmin.serializers import HubRouteAdminSerializer, ZoneRatesAdminSerializer, OrderAdminSerializer, \
    ZoneCreateSerializer
from geo.models import Zone, State
from geo.serializers import ZoneSerializer, ZoneShortSerializer
from order.models import Order
from route.models import HubRoute
from utils.views.mixins import FullnessMixin
from route.serializers import HubRouteShortSerializer


class RouteView(ModelViewSet, FullnessMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = HubRouteAdminSerializer
    queryset = HubRoute.objects.all()

    def get_queryset(self):
        fullness = self.fullness()
        if fullness == self.FullnessMode.FULL:
            return super().get_queryset().select_related('source', 'destination', 'timetable')
        if fullness == self.FullnessMode.SHORT:
            return super().get_queryset().select_related('source', 'destination')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HubRouteAdminSerializer
        fullness = self.fullness()
        if fullness == self.FullnessMode.FULL:
            return HubRouteAdminSerializer
        else:
            return HubRouteShortSerializer


class ZoneViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ZoneRatesAdminSerializer
    queryset = Zone.objects.all()

    @action(detail=False, methods=['get'], name='Zone summary', url_path='summary', url_name='zone-summary')
    def zone_summary(self, request):
        res = []
        zones = Zone.objects.annotate(
            states_count=Count('states', distinct=True),
            city_count=Count('states__cities', distinct=True)
        )
        for zone in zones.all():
            zone_dict = {
                'zone': ZoneSerializer(instance=zone).data,
                'state_count': zone.states_count,
                'city_count': zone.city_count
            }
            res.append(zone_dict)
        return Response(data=res)

    @action(detail=True, methods=['post'], name='Add states to zone', url_path='states/add',
            url_name='add-state-to-zone')
    def add_state(self, request, pk):
        try:
            state_id = request.data['state_id']
        except KeyError:
            body = {'state_id': 'state_id is required'}
            return Response(data=body, status=HTTP_400_BAD_REQUEST)
        try:
            state = State.objects.get(id=state_id)
        except State.DoesNotExist:
            body = {'state_id': f'No state with id {state_id}'}
            return Response(data=body, status=HTTP_400_BAD_REQUEST)
        zone = self.get_object()
        state.zone = zone
        state.save()
        return Response(data={'status': '200'}, status=HTTP_200_OK)

    @action(detail=True, methods=['post'], name='Remove state from zone', url_path='states/delete',
            url_name='remove-state-from-zone')
    def remove_state(self, request, pk):
        try:
            state_id = request.data['state_id']
        except KeyError:
            body = {'state_id': 'state_id is required'}
            return Response(data=body, status=HTTP_400_BAD_REQUEST)
        try:
            state = State.objects.get(id=state_id)
        except State.DoesNotExist:
            body = {'state_id': f'No state with id {state_id}'}
            return Response(data=body, status=HTTP_400_BAD_REQUEST)
        zone = self.get_object()
        if state.zone != zone:
            body = {'info': 'state does not belong to zone'}
            return Response(data=body, status=HTTP_400_BAD_REQUEST)
        state.zone = None
        state.save()
        return Response(data={'status': '200'}, status=HTTP_200_OK)


class ZoneCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ZoneCreateSerializer
    queryset = HubRoute.objects.all()


class OrderViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderAdminSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        order_query = Order.objects.prefetch_related(
            'path__routes',
            'path__routes__destination',
            'path__routes__source',
        ).select_related(
            'agent',
            'path',
            'good',
            'special'
        )
        return order_query.order_by(F('time_stamp').desc())[:30]


class CustomsEditView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            text = request.data['text']
        except KeyError:
            return Response(data={'text': 'text is required'}, status=HTTP_400_BAD_REQUEST)

        c = Customs.get()
        c.text = text
        c.save()
        return Response(data={'status': 'success'}, status=HTTP_200_OK)


class PingView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response(data={'version': '0.0.1-beta'})
