from time import time

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from geo.filters import CityFilter, StateFilter
from geo.models import Zone, Country, State, City
from geo.serializers import ZoneSerializer, CountrySerializer, StateSerializer, CitySerializer, CityShortSerializer
from utils.enums import PlaceType


class ZoneViewSet(ModelViewSet):
    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()


class CountryViewSet(ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class StateViewSet(ModelViewSet):
    serializer_class = StateSerializer
    filter_backends = [StateFilter]
    queryset = State.objects.all()


class CityViewSet(ModelViewSet):
    serializer_class = CitySerializer
    filter_backends = [CityFilter]
    queryset = City.objects.all()

    @action(detail=False, methods=['get'], name='short', url_name='short', url_path='short')
    def list_short(self, request):
        queryset = self.filter_queryset(City.objects.values('name', 'id', 'state_id'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CityShortSerializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CityShortSerializer(queryset, many=True)
        return Response(serializer.data)
