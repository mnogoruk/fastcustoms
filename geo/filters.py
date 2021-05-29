from rest_framework import filters


class CityFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        params = request.query_params

        state_slug = params.get('state')
        country_slug = params.get('country')
        zone_slug = params.get('zone')

        if state_slug:
            queryset = queryset.filter(state__slug=state_slug)
        if country_slug:
            queryset = queryset.filter(state__country__slug=country_slug)
        if zone_slug:
            queryset = queryset.filter(state__country__zone__slug=zone_slug)

        return queryset.order_by('name')
