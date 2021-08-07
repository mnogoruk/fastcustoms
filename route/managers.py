from django.db import transaction
from django.db.models import Manager, Sum, Count, Q, QuerySet

from geo.models import Zone, Country, City
from utils.enums import PlaceType, RouteType


class HubRouteQuerySet(QuerySet):
    def source_in_zone(self, zone: Zone):
        return self.filter(
            source__state__zone=zone,
        )

    def dest_in_zone(self, zone: Zone):
        return self.filter(
            destination__state__zone=zone
        )


class HubRouteBaseManager(Manager):
    def with_additional_services_cost(self):
        return self.annotate(additional_services_cost=Sum('additional_services__price'))

    def routes_related_to_city(self, city: City):
        return self.filter(source=city).union(self.filter(destionation=city))

    def src_count_by_type(self, source: City, r_type: str):
        qss = self.filter(source=source, type=r_type)
        return qss.count()

    def dst_count_by_type(self, dest: City, r_type: str):
        qsd = self.filter(destination=dest, type=r_type)
        return qsd.count()


HubRouteManager = HubRouteBaseManager.from_queryset(HubRouteQuerySet)


class PathCreatableManager(Manager):

    def create(self, total_distance, total_duration, total_cost, routes):
        with transaction.atomic():
            path = self.model.objects.create(total_distance=total_distance,
                                             total_duration_min=total_duration['min'],
                                             total_duration_max=total_duration['max'],
                                             total_cost=total_cost)
            for route_data in routes:
                if not route_data['is_hub']:
                    route_data.pop('distance')
                    route_data.pop('duration')
                    path.routes.create(**route_data)
                else:
                    route_data['_distance'] = route_data.pop('distance')
                    route_data['_duration'] = route_data.pop('duration')
                    path.routes.create(**route_data)
        return path
