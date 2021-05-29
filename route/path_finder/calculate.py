import datetime
from typing import Union

from django.db import connection

from geo.models import City
from goods.models import Good
from map.API import MapAPI
from route.models import HubRoute, AuxiliaryRoute
from route.path_finder.models import Path, PathConclusion
from route.path_finder.raw_queries import ROUTES_VIA_WAYPOINT_ZONE_QUERY, ROUTES_VIA_WAYPOINT_COUNTRY_QUERY
from utils.enums import RouteType, RateType
from route import models


class PathService:

    @classmethod
    def find(cls, source: City, dest: City) -> PathConclusion:
        hub_routes = cls._select_by_country(source, dest)
        if len(hub_routes) == 0:
            hub_routes = cls._select_by_zone(source, dest)

        # hub_routes += cls.routes_via_waypoint(source_id=source.id, destination_id=dest.id)

        print(hub_routes)
        if len(hub_routes) == 0:
            return PathConclusion(source=source, destination=dest)

        hub_sources = [route[0].source for route in hub_routes]
        hub_destinations = [route[-1].destination for route in hub_routes]

        source_route_data = MapAPI.distance_duration([source], hub_sources)
        destination_route_data = MapAPI.distance_duration(hub_destinations, [dest])

        return cls._path(source_route_data, destination_route_data, hub_routes, source, dest)

    @classmethod
    def calculate(cls, path: Union[Path, models.Path], good: Good):

        total_cost = 0
        total_duration = 0
        total_distance = 0

        if isinstance(path, models.Path):
            routes = path.hub_routes.all() + path.auxiliary_routes.all()
        else:
            routes = path.routes
        for route in routes:

            if route.is_hub:
                cost = cls.cost_of_hub_route(route, good)
            else:
                cost = cls.cost_of_auxiliary_route(route, good)

            total_cost += cost * route.distance
            total_distance += route.distance
            total_duration += route.duration

        path.total_duration = total_duration
        path.total_distance = total_distance
        path.total_cost = total_cost

        return path

    @classmethod
    def _path(cls,
              source_route_data,
              destination_route_data,
              hub_routes,
              source,
              dest
              ) -> PathConclusion:

        path_conclusion = PathConclusion(source=source, destination=dest)

        hub_routes_count = len(hub_routes)

        for i in range(hub_routes_count):
            if source_route_data[i][2] != 0 or destination_route_data[i][2] != 0:
                # can't build path, because there is error in route matrix.
                continue
            path = Path()
            hub_route = hub_routes[i]

            if source.id != hub_route[0].source_id:
                begin_route = AuxiliaryRoute(
                    source=source,
                    destination=hub_route[0].source,
                    type=RouteType.TRUCK.value,
                )
                begin_route.distance = source_route_data[i][0]
                begin_route.duration = source_route_data[i][1]
                path.routes.append(begin_route)

            for route in hub_route:
                path.routes.append(route)

            if dest.id != hub_route[-1].destination_id:
                end_route = AuxiliaryRoute(
                    source=hub_route[-1].destination,
                    destination=dest,
                    type=RouteType.TRUCK.value,
                )
                end_route.distance = destination_route_data[i][0]
                end_route.duration = destination_route_data[i][1]
                path.routes.append(end_route)

            path_conclusion.paths.append(path)

        return path_conclusion

    @classmethod
    def _select_by_zone(cls, source: City, dest: City):
        source_country = source.state.country
        dest_country = dest.state.country

        if source_country is None or dest_country is None:
            return []

        routes = [(route,) for route in HubRoute.objects.find_by_country(source_country, dest_country)]
        routes += cls.routes_via_waypoint_country(source_country.id, dest_country.id)

        return routes

    @classmethod
    def _select_by_country(cls, source: City, dest: City):
        source_zone = source.state.country.zone
        dest_zone = dest.state.country.zone

        if source_zone is None or dest_zone is None:
            return []
        routes = [(route,) for route in HubRoute.objects.find_by_zone(source_zone, dest_zone)]
        routes += cls.routes_via_waypoint_zone(source_zone.id, dest_zone.id)

        return routes

    @classmethod
    def cost_of_hub_route(cls, route: HubRoute, good: Good):

        cost_ldm, cost_size, cost_mass = cls._cost_of_ratable(route, good)

        return max(cost_ldm, cost_size, cost_mass)

    @classmethod
    def cost_of_auxiliary_route(cls, route: AuxiliaryRoute, good: Good):
        zone = route.source.state.country.zone
        cost_ldm, cost_size, cost_mass = cls._cost_of_ratable(zone, good)

        return max(cost_ldm, cost_size, cost_mass)

    @classmethod
    def routes_via_waypoint_zone(cls, source_id, destination_id):
        with connection.cursor() as cursor:
            cursor.execute(ROUTES_VIA_WAYPOINT_ZONE_QUERY, [source_id, destination_id])
            rows = cursor.fetchall()
        return cls.to_routes(rows)

    @classmethod
    def routes_via_waypoint_country(cls, source_id, destination_id):
        with connection.cursor() as cursor:
            cursor.execute(ROUTES_VIA_WAYPOINT_COUNTRY_QUERY, [source_id, destination_id])
            rows = cursor.fetchall()
        return cls.to_routes(rows)

    @classmethod
    def to_routes(cls, ids):
        routes = []
        for pair in ids:
            routes.append((HubRoute.objects.get(id=pair[0]), HubRoute.objects.get(id=pair[1])))

        return routes

    @classmethod
    def _cost_of_ratable(cls, ratable, good):
        try:
            rate_ldm = ratable.rates.get(
                range_from__lte=good.total_ldm,
                range_to__gt=good.total_ldm,
                type=RateType.LDM.value
            )
        except Exception:
            cost_ldm = 0
        else:
            cost_ldm = rate_ldm.price_per_unit * good.total_ldm
        try:
            rate_size = ratable.rates.get(
                range_from__lte=good.total_volume,
                range_to__gt=good.total_volume,
                type=RateType.SIZE.value
            )
        except Exception:
            cost_size = 0
        else:
            cost_size = rate_size.price_per_unit * good.total_volume
        try:
            rate_mass = ratable.rates.get(
                range_from__lte=good.total_mass,
                range_to__gt=good.total_mass,
                type=RateType.MASS.value
            )
        except Exception:
            cost_mass = 0
        else:
            cost_mass = rate_mass.price_per_unit * good.total_mass
        return cost_ldm, cost_size, cost_mass
