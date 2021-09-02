import datetime
import logging
from typing import Union, List

from django.db import connection
from django.db.models import Sum

from geo.models import City, Zone
from map.here.api import MapAPI
from route.models import HubRoute, RouteInPath
from route.service import models as dataclass
from route.service.models import PathDuration, Good, Special
from route.service.raw_queries import ROUTES_VIA_WAYPOINT_ZONE_QUERY
from utils.enums import RouteType, RateType, PlaceType
from route import models
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger('route.service')


class PathService:
    API_CLASS = MapAPI()

    @classmethod
    def set_map_api_class(cls, api_class):
        cls.API_CLASS = api_class

    @classmethod
    def paths(cls, source: City, dest: City, source_type, destination_type) -> list:

        # better if source and dest objects all have prefetched zone instance
        hub_routes = cls.hub_routes(source, dest, source_type, destination_type)

        if len(hub_routes) == 0:
            return []

        # first and last places in only hub route path
        hub_sources = [route[0].source for route in hub_routes]
        hub_destinations = [route[-1].destination for route in hub_routes]

        # calculate distances and durations of auxiliary routes
        source_route_data = cls.API_CLASS.distance_duration([source], hub_sources)
        destination_route_data = cls.API_CLASS.distance_duration(hub_destinations, [dest])

        # combine all it
        paths = cls.build_paths(source_route_data, destination_route_data, hub_routes, source, dest, source_type,
                                destination_type)
        return cls.excluded_circles(paths)

    @classmethod
    def excluded_circles(cls, paths: List[dataclass.Path]):
        correct_paths = []
        for i, path in enumerate(paths):
            sources = []
            for route in path.routes:
                if route.destination in sources:
                    break
                sources.append(route.source)
            else:
                correct_paths.append(path)
        return correct_paths

    @classmethod
    def build_paths(cls,
                    source_route_data,
                    destination_route_data,
                    hub_routes,
                    source,
                    dest,
                    source_type,
                    destination_type
                    ) -> list:

        paths = []

        hub_routes_count = len(hub_routes)

        for i in range(hub_routes_count):
            if source_route_data[i][2] != 0 or destination_route_data[i][2] != 0:
                # can't build path, because there is error in route matrix.
                logger.warning(f'error in distance matrix. {source.name}({source.id}) - {dest.name}({dest.id}) | '
                               f'f{source_route_data} | '
                               f'index: {i}')
                continue

            path = dataclass.Path()
            hub_route = hub_routes[i]

            if source_type == PlaceType.CITY.value:
                if hub_route[0].source_id != source.id:
                    begin_route = RouteInPath(
                        source=source,
                        destination=hub_route[0].source,
                        type=RouteType.TRUCK.value,
                        is_hub=False
                    )
                    begin_route.distance = source_route_data[i][0]
                    begin_route.duration = source_route_data[i][1]
                    path.routes.append(begin_route)

                else:
                    begin_route = RouteInPath(
                        source=source,
                        destination=source,
                        type=RouteType.TRUCK.value,
                        is_hub=False
                    )
                    begin_route.distance = 0
                    begin_route.duration = 0
                    path.routes.append(begin_route)

            else:
                if hub_route[0].source_id != source.id:
                    continue

            for route in hub_route:
                path.routes.append(route)

            if destination_type == PlaceType.CITY.value:
                if dest.id != hub_route[-1].destination_id:
                    end_route = RouteInPath(
                        source=hub_route[-1].destination,
                        destination=dest,
                        type=RouteType.TRUCK.value,
                        is_hub=False
                    )
                    end_route.distance = destination_route_data[i][0]
                    end_route.duration = destination_route_data[i][1]
                    path.routes.append(end_route)
                else:
                    end_route = RouteInPath(
                        source=dest,
                        destination=dest,
                        type=RouteType.TRUCK.value,
                        is_hub=False
                    )
                    end_route.distance = 0
                    end_route.duration = 0
                    path.routes.append(end_route)
            else:
                if hub_route[-1].destination_id != dest.id:
                    continue

            paths.append(path)

        return paths

    @classmethod
    def calculate(cls, path: Union[dataclass.Path, models.Path], good: Good, special: Special = Special()):
        total_cost = 0
        total_duration = PathDuration(1, 1)
        total_distance = 0

        logger.info({'calculate': {'good': good}})

        if special.departure_date is None:
            departure_date_best = datetime.date.today()
            departure_date_worst = datetime.date.today()
        else:
            departure_date_best = special.departure_date
            departure_date_worst = special.departure_date

        if isinstance(path, models.Path):
            routes = path.routes.all()
        elif isinstance(path, dataclass.Path):
            routes = path.routes
        else:
            raise ValueError(
                f"path must be route.service.models.Path or route.models.Path instance. Got {type(path)} instead"
            )
        for route in routes:
            if route.is_hub:
                cost = cls.cost_of_hub_route(route, good)
                logger.info({'calculate': {'cost_of_hub_route': cost}})
            else:
                cost = cls.cost_of_auxiliary_route(route, good)
                logger.info({'calculate': {'cost_of_auxiliary_route': cost}})

            total_cost += cost
            total_distance += route.distance

            if route.is_hub:
                duration_best = route.duration_from_department(departure_date_best)
                duration_worst = route.duration_from_department(departure_date_worst + datetime.timedelta(days=1))
                total_duration.min += duration_best
                total_duration.max += duration_worst

                departure_date_best += datetime.timedelta(days=duration_best)
                departure_date_worst += datetime.timedelta(days=duration_worst)

            else:
                total_duration.min += route.duration
                total_duration.max += route.duration + 1

        path.total_duration = total_duration
        path.total_distance = total_distance
        path.total_cost = total_cost

        return path

    @classmethod
    def hub_routes(cls, source: City, dest: City, source_type=PlaceType.default().value,
                   destination_type=PlaceType.default().value):
        """ Search all routes from source zone to destination zone. U """
        source_zone = source.state.zone
        dest_zone = dest.state.zone

        routes_query = HubRoute.objects.filter(active=True)

        if source_zone is None or dest_zone is None:
            return []

        if source_type == PlaceType.CITY.value:
            routes_query = routes_query.source_in_zone(zone=source_zone)
        else:
            routes_query = routes_query.filter(source=source).filter(source__types__contains=[source_type])

        if destination_type == PlaceType.CITY.value:
            routes_query = routes_query.dest_in_zone(zone=dest_zone)
        else:
            routes_query = routes_query.filter(destination=dest).filter(destination__types__contains=[destination_type])

        routes = [(route,) for route in routes_query.all()]

        routes_via_waypoint = cls.routes_via_waypoint_zone(source_zone, dest_zone, source_type, destination_type)

        routes += routes_via_waypoint
        return routes

    @classmethod
    def cost_of_hub_route(cls, route: HubRoute, good: Good):
        cost_ldm, cost_size, cost_mass = cls.cost_by_ratable(route, good)
        logger.info({'cost_of_hub_route': {'cost_ldm': cost_ldm, 'cost_size': cost_size, 'cost_mass': cost_mass,
                                           'route': route}})
        cost_service = cls.cost_by_services(route, good)
        logger.info({'cost_of_hub_route': {'cost_service': cost_service}})
        cost = max(cost_ldm, cost_size, cost_mass) * route.distance + cost_service
        if cost < float(route.minimal_price):
            cost = float(route.minimal_price)
        price = cost * route.markup
        return price

    @classmethod
    def cost_of_auxiliary_route(cls, route: RouteInPath, good: Good):
        zone = route.source.state.zone
        pricing_info = zone.pricing_info
        distance = route.distance

        cost_ldm, cost_size, cost_mass = cls.cost_by_ratable(zone, good)
        logger.info({'cost_of_auxiliary_route': {'cost_ldm': cost_ldm, 'cost_size': cost_size, 'cost_mass': cost_mass,
                                                 'route': route}})

        cost = max(cost_ldm, cost_size, cost_mass) * distance
        if cost < float(pricing_info.minimal_price):
            cost = float(pricing_info.minimal_price)
        price = cost * pricing_info.markup
        return price

    @classmethod
    def routes_via_waypoint_zone(cls, source_zone, destination_zone, source_type=PlaceType.default().value,
                                 destination_type=PlaceType.default().value):
        with connection.cursor() as cursor:
            cursor.execute(ROUTES_VIA_WAYPOINT_ZONE_QUERY,
                           [source_zone.id, source_type, destination_zone.id, destination_type])
            rows = cursor.fetchall()
        return cls.to_routes(rows)

    @classmethod
    def to_routes(cls, ids):
        routes = []
        for pair in ids:
            routes.append((HubRoute.objects.get(id=pair[0]), HubRoute.objects.get(id=pair[1])))

        return routes

    @classmethod
    def cost_by_services(cls, route: HubRoute, good: Good):
        services_cost = route.additional_services.aggregate(sum=Sum('price'))['sum'] or 0
        ranked_services = route.ranked_services
        services_cost = float(services_cost)
        for service in ranked_services.all():
            if service.rank_type == RateType.MASS.value:
                services_cost += float(service.price_per_unit) * float(good.total_mass)
            elif service.rank_type == RateType.SIZE.value:
                services_cost += float(service.price_per_unit) * float(good.total_volume)
            elif service.rank_type == RateType.LDM.value:
                services_cost += float(service.price_per_unit) * float(good.total_ldm)

        return services_cost

    @classmethod
    def cost_by_ratable(cls, ratable, good):
        try:
            rate_ldm = ratable.rates.get(
                range_from__lte=good.total_ldm,
                range_to__gt=good.total_ldm,
                type=RateType.LDM.value
            )
        except ObjectDoesNotExist:
            cost_ldm = 0
        else:
            cost_ldm = float(rate_ldm.price_per_unit) * good.total_ldm
        try:
            rate_size = ratable.rates.get(
                range_from__lte=good.total_volume,
                range_to__gt=good.total_volume,
                type=RateType.SIZE.value
            )
        except ObjectDoesNotExist:
            cost_size = 0
        else:
            cost_size = float(rate_size.price_per_unit) * good.total_volume
        try:
            rate_mass = ratable.rates.get(
                range_from__lte=good.total_mass,
                range_to__gt=good.total_mass,
                type=RateType.MASS.value
            )
        except ObjectDoesNotExist:
            cost_mass = 0
        else:
            cost_mass = float(rate_mass.price_per_unit) * good.total_mass
        return cost_ldm, cost_size, cost_mass
