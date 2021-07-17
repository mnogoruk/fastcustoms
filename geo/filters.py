from rest_framework import filters

from utils.enums import PlaceType


class CityFilter(filters.BaseFilterBackend):

    def filter_by_geo(self, request, queryset, view):
        params = request.query_params

        state_name = params.get('state')
        country_name = params.get('country')
        zone_name = params.get('zone')

        if state_name:
            queryset = queryset.filter(state__name=state_name)
        if country_name:
            queryset = queryset.filter(state__country__name=country_name)
        if zone_name:
            queryset = queryset.filter(state__zone__name=zone_name)

        return queryset

    def filter_by_type(self, request, queryset, view):
        params = request.query_params

        place_type = params.get('type', None)

        if place_type is None:
            return queryset
        return queryset.filter(types__contained_by=[place_type])

    def filter_queryset(self, request, queryset, view):
        queryset = self.filter_by_geo(request, queryset, view)
        queryset = self.filter_by_type(request, queryset, view)
        return queryset.order_by('name')


class StateFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = request.query_params

        country_name = params.get('country')
        zone_name = params.get('zone')

        if country_name:
            queryset = queryset.filter(country__name=country_name)
        if zone_name:
            queryset = queryset.filter(zone__name=zone_name)

        return queryset.order_by('name')
