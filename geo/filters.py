from rest_framework import filters


class CityFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        params = request.query_params

        state_name = params.get('state')
        country_name = params.get('country')
        zone_name = params.get('zone')
        place_type = params.get('type', None)

        if state_name:
            queryset = queryset.filter(state__name=state_name)
        if country_name:
            queryset = queryset.filter(state__country__name=country_name)
        if zone_name:
            queryset = queryset.filter(state__zone__name=zone_name)

        if place_type:
            queryset = queryset.filter(types__contains=[place_type])

        return queryset.order_by('name')


class StateFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = request.query_params

        country_name = params.get('country')
        zone_name = params.get('zone')

        empty = params.get('empty')
        if empty in ('on', 'True', '', True, '1', 'true'):
            empty = True
        else:
            empty = False
        if empty:
            return queryset.filter(zone__isnull=True).order_by('name')

        if country_name:
            queryset = queryset.filter(country__name=country_name)
        if zone_name:
            queryset = queryset.filter(zone__name=zone_name)

        return queryset.order_by('name')
