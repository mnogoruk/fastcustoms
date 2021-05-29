import time

from django.db.models import Count, Max
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from geo.filters import CityFilter
from geo.models import Zone, Country, State, City
from geo.serializers import ZoneSerializer, CountrySerializer, StateSerializer, CitySerializer


class ZoneViewSet(ModelViewSet):
    serializer_class = ZoneSerializer
    queryset = Zone.objects.all()


class CountryViewSet(ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class StateViewSet(ModelViewSet):
    serializer_class = StateSerializer
    queryset = State.objects.all()


class CityViewSet(ModelViewSet):
    serializer_class = CitySerializer
    filter_backends = [CityFilter]
    queryset = City.objects.all()
