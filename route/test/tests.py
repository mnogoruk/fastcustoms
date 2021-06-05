from copy import copy
from random import randint
from typing import Union

from rest_framework.test import APITestCase

from geo.models import City, Country
from route.models import HubRoute, RouteTimeTable, AuxiliaryRoute
from route.service.calculate import PathService
from route.service.models import Path
from route.test.api import TestMapAPI


class PathServiceTest(APITestCase):
    MAIN_ROUTE_DISTANCE = 1000000
    MAIN_ROUTE_DURATION = 1000

    VIA_WAYPOINT_DISTANCE = 500000
    VIA_WAYPOINT_DURATION = 500

    @classmethod
    def setUpClass(cls):
        PathService.set_map_api_class(TestMapAPI)
        AuxiliaryRoute.set_map_api_class(TestMapAPI)
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.country_ru = Country.objects.get(name='Russia')
        cls.country_de = Country.objects.get(name='Germany')
        cls.country_fr = Country.objects.get(name='France')
        cls.country_pl = Country.objects.get(name='Poland')

        cls.cities_ru = [city for city in
                         City.objects.filter(state__country=cls.country_ru).order_by('?')[:10]]  # sources
        cls.cities_de = [city for city in
                         City.objects.filter(state__country=cls.country_de).order_by('?')[:10]]  # waypoints
        cls.cities_fr = [city for city in
                         City.objects.filter(state__country=cls.country_fr).order_by('?')[:10]]  # waypoints
        cls.cities_pl = [city for city in
                         City.objects.filter(state__country=cls.country_pl).order_by('?')[:10]]  # destinations

        cls.waypoints = cls.cities_de + cls.cities_fr

        cls.directed_routes = []

        cls.directed_routes.append(cls.createHubRoute(cls.cities_ru[0], cls.cities_pl[0], cls.createDefaultTimeTable()))
        cls.directed_routes.append(cls.createHubRoute(cls.cities_ru[1], cls.cities_pl[1], cls.createDefaultTimeTable()))

        cls.via_routes = []

        cls.via_routes.append(
            (
                cls.createHubRoute(cls.cities_ru[3], cls.waypoints[0], cls.createDefaultTimeTable()),
                cls.createHubRoute(cls.waypoints[0], cls.cities_pl[3], cls.createDefaultTimeTable())
            )
        )
        cls.via_routes.append(
            (
                cls.createHubRoute(cls.cities_ru[4], cls.waypoints[1], cls.createDefaultTimeTable()),
                cls.createHubRoute(cls.waypoints[1], cls.cities_pl[4], cls.createDefaultTimeTable())
            )
        )

    @classmethod
    def createHubRoute(cls, source, destination, timetable):
        return HubRoute.objects.create(
            source=source,
            destination=destination,
            timetable=timetable,
            type='AIR',
            distance=cls.MAIN_ROUTE_DISTANCE,
            duration=cls.MAIN_ROUTE_DURATION,
        )

    @classmethod
    def createDefaultTimeTable(cls):
        return RouteTimeTable.objects.create(
            weekdays=[1 for _ in range(7)],
            preparation_period=0
        )

    def testPathFinding(self):
        # from Russia to Poland all routes test

        source = self.cities_ru[0]
        dest = self.cities_pl[0]

        real_paths = self.realPath(source, dest)

        calculated_paths = PathService.paths(source, dest)

        for i, path1 in enumerate(calculated_paths):
            for j, path2 in enumerate(real_paths):
                if self.pathRoutesEquals(path1, path2):
                    real_paths.pop(j)
                    break
            else:
                raise self.failureException(f"Odd path: {path1}")

        if len(real_paths) != 0:
            raise self.failureException(f"Missing paths: {real_paths}")

    def realPath(self, source, destination):
        return [
            Path(routes=[
                self.directed_routes[0]
            ]),
            Path(routes=[
                AuxiliaryRoute(source=source, destination=self.directed_routes[1].source),
                self.directed_routes[1],
                AuxiliaryRoute(source=self.directed_routes[1].destination, destination=destination)
            ]),
            Path(routes=[
                AuxiliaryRoute(source=source, destination=self.via_routes[0][0].source),
                self.via_routes[0][0],
                self.via_routes[0][1],
                AuxiliaryRoute(source=self.via_routes[0][1].destination, destination=destination)
            ]),
            Path(routes=[
                AuxiliaryRoute(source=source, destination=self.via_routes[1][0].source),
                self.via_routes[1][0],
                self.via_routes[1][1],
                AuxiliaryRoute(source=self.via_routes[1][1].destination, destination=destination)
            ])
        ]

    def assertPathRoutesEquals(self, path_origin: Path, path_check: Path, **kwargs):
        self.assertTrue(self.pathRoutesEquals(path_origin, path_check), **kwargs)

    def assertEqualRoute(self, route_origin: Union[HubRoute, AuxiliaryRoute],
                         route_check: Union[HubRoute, AuxiliaryRoute], **kwargs):
        self.assertTrue(self.routeEquals(route_origin, route_check), **kwargs)

    def assertRouteIn(self, route, container, **kwargs):
        self.assertTrue(self.routeIn(route, container), **kwargs)

    def pathRoutesEquals(self, path1: Path, path2: Path):
        routes1 = copy(path1.routes)
        routes2 = copy(path2.routes)

        for i, route1 in enumerate(routes1):
            for j, route2 in enumerate(routes2):
                if self.routeEquals(route1, route2):
                    routes2.pop(j)
                    break
            else:
                return False

        if len(routes2) != 0:
            return False
        else:
            return True

    def routeEquals(self, route1: Union[HubRoute, AuxiliaryRoute], route2: Union[HubRoute, AuxiliaryRoute]):
        if type(route1) != type(route2):
            return False
        if route1.source != route2.source:
            return False
        if route1.destination != route2.destination:
            return False
        if route1.type != route2.type:
            return False
        if route1.distance != route2.distance:
            return False
        return True

    def routeIn(self, route, container):
        for origin in container:
            if self.routeEquals(route, origin):
                return True
        return False
