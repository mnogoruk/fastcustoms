from copy import copy
from random import randint
from typing import Union

from rest_framework.test import APITestCase

from geo.models import City, Country
from goods.models import Good
from pricing.models import RouteRate, ServiceAdditional, ServiceRanked
from route.models import HubRoute, RouteTimeTable, AuxiliaryRoute
from route.service.calculate import PathService
from route.service.models import Path
from route.test.api import TestMapAPI
from utils.enums import RateType


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


class DefaultCreate:
    DEFAULT_ROUTE_DISTANCE = 1000
    DEFAULT_ROUTE_DURATION = 1000
    DEFAULT_RANGE_FROM = 0
    DEFAULT_RANGE_TO = 10000

    DEFAULT_PRICE_PER_UNIT = 0.0122
    DEFAULT_VALUE = 124.4

    DEFAULT_SERVICE_PRICE = 123

    DEFAULT_MASS = 123
    DEFAULT_LDM = 341
    DEFAULT_SIZE = 542

    DEFAULT_RATE_TYPE = RateType.__default__

    def create_route(self):
        source = City.objects.order_by('?').first()
        destination = City.objects.order_by('?').first()

        return HubRoute.objects.create(
            source=source,
            destination=destination,
            type='AIR',
            distance=self.DEFAULT_ROUTE_DISTANCE,
            duration=self.DEFAULT_ROUTE_DURATION,
        )

    def crete_rate(self, route, r_type, ppu=DEFAULT_PRICE_PER_UNIT, rf=DEFAULT_RANGE_FROM, rt=DEFAULT_RANGE_TO):
        return RouteRate.objects.create(
            route=route,
            range_from=rf,
            range_to=rt,
            type=r_type,
            price_per_unit=ppu
        )

    def create_additional_service(self, route, price=DEFAULT_SERVICE_PRICE):
        return ServiceAdditional.objects.create(route=route, price=price, name='default')

    def create_ranked_service(self, route, r_type, ppu=DEFAULT_PRICE_PER_UNIT):
        return ServiceRanked.objects.create(route=route, price_per_unit=ppu, rank_type=r_type, name='default')

    def create_good(self, value=DEFAULT_VALUE, r_type=DEFAULT_RATE_TYPE):
        if r_type == RateType.MASS.value:
            return Good(total_mass=value, total_ldm=0, total_volume=0)
        elif r_type == RateType.LDM.value:
            return Good(total_mass=0, total_ldm=value, total_volume=0)
        elif r_type == RateType.SIZE.value:
            return Good(total_mass=0, total_ldm=0, total_volume=value)
        else:
            raise Exception(f"Wrong type got {r_type}")


class DefaultCalculationSingleTypeSingleRangeTest(APITestCase, DefaultCreate):

    def test_mass(self):
        route = self.create_route()
        self.crete_rate(route, r_type=RateType.MASS.value)
        good = Good(total_mass=self.DEFAULT_VALUE, total_ldm=0, total_volume=0)

        cost_ldm, cost_size, cost_mass = PathService.cost_by_ratable(route, good)

        real_cost_mass = self.DEFAULT_PRICE_PER_UNIT * self.DEFAULT_VALUE

        self.assertEqual(float(cost_mass), float(real_cost_mass))

    def test_ldm(self):
        route = self.create_route()
        self.crete_rate(route, r_type=RateType.LDM.value)
        good = Good(total_mass=0, total_ldm=self.DEFAULT_VALUE, total_volume=0)

        cost_ldm, cost_size, cost_mass = PathService.cost_by_ratable(route, good)

        real_cost_ldm = self.DEFAULT_PRICE_PER_UNIT * self.DEFAULT_VALUE

        self.assertEqual(float(cost_ldm), float(real_cost_ldm))

    def test_size(self):
        route = self.create_route()
        self.crete_rate(route, r_type=RateType.SIZE.value)
        good = Good(total_mass=0, total_ldm=0, total_volume=self.DEFAULT_VALUE)

        cost_ldm, cost_size, cost_mass = PathService.cost_by_ratable(route, good)

        real_cost_size = self.DEFAULT_PRICE_PER_UNIT * self.DEFAULT_VALUE

        self.assertEqual(float(cost_size), float(real_cost_size))


class DefaultCalculationSingleTypeMultipleRangeTest(APITestCase, DefaultCreate):
    DEFAULT_RT_1 = 100
    DEFAULT_RT_2 = 200
    DEFAULT_RT_3 = 1000

    DEFAULT_RF_1 = 0
    DEFAULT_RF_2 = DEFAULT_RT_1
    DEFAULT_RF_3 = DEFAULT_RT_2

    DEFAULT_PPU_1 = 1
    DEFAULT_PPU_2 = 2
    DEFAULT_PPU_3 = 3

    def default_rate_check(self, value, r_type):
        route = self.create_route()

        ppu1 = self.DEFAULT_PPU_1
        ppu2 = self.DEFAULT_PPU_2
        ppu3 = self.DEFAULT_PPU_3

        self.crete_rate(route, r_type=r_type, rf=self.DEFAULT_RF_1, rt=self.DEFAULT_RT_1, ppu=ppu1)
        self.crete_rate(route, r_type=r_type, rf=self.DEFAULT_RF_2, rt=self.DEFAULT_RT_2, ppu=ppu2)
        self.crete_rate(route, r_type=r_type, rf=self.DEFAULT_RF_3, rt=self.DEFAULT_RT_3, ppu=ppu3)

        good = self.create_good(value, r_type)

        cost_ldm, cost_size, cost_mass = PathService.cost_by_ratable(route, good)

        ppu = ppu1 if value < self.DEFAULT_RT_1 else (ppu2 if value < self.DEFAULT_RT_2 else ppu3)
        real_cost = ppu * value
        if r_type == RateType.MASS.value:
            self.assertEqual(float(cost_mass), float(real_cost))
        elif r_type == RateType.LDM.value:
            self.assertEqual(float(cost_ldm), float(real_cost))
        elif r_type == RateType.SIZE.value:
            self.assertEqual(float(cost_size), float(real_cost))
        else:
            raise Exception(f"Wrong type got {r_type}")

    def test_range_mass_1(self):
        self.default_rate_check(50, RateType.MASS.value)

    def test_range_mass_2(self):
        self.default_rate_check(150, RateType.MASS.value)

    def test_range_mass_3(self):
        self.default_rate_check(250, RateType.MASS.value)

    def test_range_ldm_1(self):
        self.default_rate_check(50, RateType.LDM.value)

    def test_range_ldm_2(self):
        self.default_rate_check(150, RateType.LDM.value)

    def test_range_ldm_3(self):
        self.default_rate_check(250, RateType.LDM.value)

    def test_range_size_1(self):
        self.default_rate_check(50, RateType.SIZE.value)

    def test_range_size_2(self):
        self.default_rate_check(150, RateType.SIZE.value)

    def test_range_size_3(self):
        self.default_rate_check(250, RateType.SIZE.value)


class DefaultCalculationMultipleTypeMultipleRangeTest(APITestCase, DefaultCreate):
    pass


class ServiceCalculationTest(APITestCase, DefaultCreate):

    def test_singe_additional_service_cost(self):
        route = self.create_route()
        price = 100
        self.create_additional_service(route, price)
        good = self.create_good(0, RateType.LDM.value)
        route.refresh_from_db()

        cost = PathService.cost_by_services(route, good)

        self.assertAlmostEqual(float(price), float(cost), places=3)

    def test_multiple_additional_service_cost(self):
        route = self.create_route()
        price1 = 100
        price2 = 123
        price3 = 431

        self.create_additional_service(route, price1)
        self.create_additional_service(route, price2)
        self.create_additional_service(route, price3)
        good = self.create_good(0, RateType.LDM.value)
        route.refresh_from_db()

        cost = PathService.cost_by_services(route, good)
        price = price1 + price2 + price3
        self.assertAlmostEqual(float(price), float(cost), places=3)

    def test_single_ranked_service_cost_mass(self):
        route = self.create_route()
        value = 1231
        mass = 34.1
        self.create_ranked_service(route, r_type=RateType.MASS.value, ppu=value)
        good = self.create_good(mass, RateType.MASS.value)
        route.refresh_from_db()

        cost = PathService.cost_by_services(route, good)
        price = mass * value
        self.assertAlmostEqual(float(price), float(cost), places=3)

    def test_single_ranked_service_cost_size(self):
        route = self.create_route()
        value = 143
        size = 34.1
        self.create_ranked_service(route, r_type=RateType.SIZE.value, ppu=value)
        good = self.create_good(size, RateType.SIZE.value)
        route.refresh_from_db()
        cost = PathService.cost_by_services(route, good)
        price = size * value
        self.assertAlmostEqual(float(price), float(cost), places=3)

    def test_single_ranked_service_cost_ldm(self):
        route = self.create_route()
        value = 1231
        ldm = 341.243
        self.create_ranked_service(route, r_type=RateType.LDM.value, ppu=value)
        good = self.create_good(ldm, RateType.LDM.value)
        route.refresh_from_db()

        cost = PathService.cost_by_services(route, good)
        price = ldm * value
        self.assertAlmostEqual(float(price), float(cost), places=3)

    def test_single_ranked_service_cost_combine(self):
        route = self.create_route()

        ldm = 234
        mass = 542
        size = 325

        value_ldm = 432
        value_mass = 52.2
        value_size = 43.2

        self.create_ranked_service(route, r_type=RateType.LDM.value, ppu=value_ldm)
        self.create_ranked_service(route, r_type=RateType.MASS.value, ppu=value_mass)
        self.create_ranked_service(route, r_type=RateType.SIZE.value, ppu=value_size)
        good = Good(total_mass=mass, total_ldm=ldm, total_volume=size)
        route.refresh_from_db()

        cost = PathService.cost_by_services(route, good)
        price = ldm * value_ldm + mass * value_mass + value_size * size
        self.assertAlmostEqual(float(price), float(cost), places=3)

    def test_combine_service_cost(self):
        route = self.create_route()

        as_value1 = 34.6
        as_value2 = 98.32

        ldm = 756.43
        mass = 323.53
        size = 324.2

        value_ldm1 = 14.65
        value_ldm2 = 432.3

        value_mass1 = 1123.4
        value_mass2 = 2141.32

        value_size1 = 321.43
        value_size2 = 343.21
        value_size3 = 3323.21

        self.create_ranked_service(route, r_type=RateType.LDM.value, ppu=value_ldm1)
        self.create_ranked_service(route, r_type=RateType.LDM.value, ppu=value_ldm2)

        self.create_ranked_service(route, r_type=RateType.MASS.value, ppu=value_mass1)
        self.create_ranked_service(route, r_type=RateType.MASS.value, ppu=value_mass2)

        self.create_ranked_service(route, r_type=RateType.SIZE.value, ppu=value_size1)
        self.create_ranked_service(route, r_type=RateType.SIZE.value, ppu=value_size2)
        self.create_ranked_service(route, r_type=RateType.SIZE.value, ppu=value_size3)

        self.create_additional_service(route, as_value1)
        self.create_additional_service(route, as_value2)
        route.refresh_from_db()

        good = Good(total_mass=mass, total_volume=size, total_ldm=ldm)
        cost = PathService.cost_by_services(route, good)
        price = as_value1 + as_value2 + (value_ldm1 + value_ldm2) * ldm + (value_mass1 + value_mass2) * mass + (
                value_size1 + value_size2 + value_size3) * size
        self.assertAlmostEqual(float(price), float(cost), places=3)


class TotalCostRouteTest(APITestCase, DefaultCreate):
    as_value1 = 34.6
    as_value2 = 98.32

    ldm = 756.43
    mass = 323.53
    size = 324.2

    value_ldm1 = 14.65
    value_ldm2 = 432.3

    value_mass1 = 1123.4
    value_mass2 = 2141.32

    value_size1 = 321.43
    value_size2 = 343.21
    value_size3 = 3323.21

    def create_services(self, route):
        self.create_ranked_service(route, r_type=RateType.LDM.value, ppu=self.value_ldm1)
        self.create_ranked_service(route, r_type=RateType.LDM.value, ppu=self.value_ldm2)

        self.create_ranked_service(route, r_type=RateType.MASS.value, ppu=self.value_mass1)
        self.create_ranked_service(route, r_type=RateType.MASS.value, ppu=self.value_mass2)

        self.create_ranked_service(route, r_type=RateType.SIZE.value, ppu=self.value_size1)
        self.create_ranked_service(route, r_type=RateType.SIZE.value, ppu=self.value_size2)
        self.create_ranked_service(route, r_type=RateType.SIZE.value, ppu=self.value_size3)

        self.create_additional_service(route, self.as_value1)
        self.create_additional_service(route, self.as_value2)

    def test_total_price_max_mass(self):
        route = self.create_route()
        self.create_services(route)
        # TODO ...
