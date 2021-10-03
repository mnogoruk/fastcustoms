from typing import List
from math import exp

from geo.models import City
from order.models import Special
from route.service.calculate import PathService
from route.service.models import PathConclusion, Box, Container, Good
from utils.enums import PlaceType
from .models import Path
import logging

DURATION_WEIGHT = 1
COST_WEIGHT = 1

logger = logging.getLogger('path_calculator')


def sort_func(path: Path, avg_cost, avg_duration):
    if avg_cost == 0:
        duration_c = 0
    else:
        duration_c = path.total_duration.max / avg_duration

    if avg_cost == 0:
        cost_c = 0
    else:
        cost_c = path.total_cost / avg_cost
    return exp(cost_c) * COST_WEIGHT + exp(duration_c) * DURATION_WEIGHT


class PathCalculator:

    def __init__(self, **data):
        self.source = self.get_place(data.pop('source', {}).pop('id'))
        self.destination = self.get_place(data.pop('destination', {}).pop('id'))
        self.source_type = data.pop('source_type', PlaceType.default().value)
        self.destination_type = data.pop('destination_type', PlaceType.default().value)
        self.good = self.built_good(good_data=data.pop('good', {}))
        self.special = self.build_special(special_data=data.pop('special', {}))

    @classmethod
    def built_good(cls, good_data):
        boxes = []
        containers = []

        for box in good_data.pop('boxes', []):
            boxes.append(
                Box(
                    length=box['length'],
                    width=box['width'],
                    height=box['height'],
                    mass=box['mass'],
                    amount=box['amount'],
                    type=box['type']
                )
            )

        for container in good_data.pop('containers', []):
            containers.append(
                Container(
                    type=container['type'],
                    amount=container['amount']
                )
            )
        good = Good(boxes=boxes, containers=containers)
        good.recalculate_params()
        return good

    @classmethod
    def build_special(cls, special_data):
        return Special(**special_data)

    @classmethod
    def get_place(cls, place_id):
        return City.objects.select_related(
            'state__zone',
        ).get(id=place_id)

    def sort_paths(self, paths: List[Path]):
        logger.warning(f'(salt) input paths: {paths}')
        if len(paths) == 0:
            return paths
        elif len(paths) == 1:
            path = paths[0]
            path.fastest = True
            path.cheapest = True
            path.optimal = True

        # for avg
        total_cost = 0
        total_duration = 0

        for p in paths:
            total_cost += p.total_cost
            total_duration += p.total_duration.max

        avg_cost = total_cost / len(paths)
        avg_duration = total_duration / len(paths)

        paths = sorted(paths, key=lambda p: sort_func(p, avg_cost, avg_duration))
        fastest = paths[0]
        cheapest = paths[0]

        fastest_ind = 0
        cheapest_ind = 0

        logger.warning(f'(salt) after sort 1: {paths}')
        for ind, path in enumerate(paths):
            if float(path.total_cost) < float(cheapest.total_cost):
                cheapest = path
                cheapest_ind = ind
                logger.warning(f'(salt) cheapest_ind: {cheapest_ind}')
                logger.warning(f'(salt) ind: {ind}')
            if float(path.total_duration.max) < float(fastest.total_duration.max):
                fastest = path
                fastest_ind = ind

        cheapest.cheapest = True
        fastest.fastest = True
        logger.warning(f'(salt) fastest: ({fastest_ind}){fastest}')
        logger.warning(f'(salt) cheapest: ({cheapest_ind}){cheapest}')
        if len(paths) > 2:
            paths[0].optimal = True

        if cheapest_ind == fastest_ind:
            if cheapest_ind > 0:
                paths.pop(cheapest_ind)
                logger.warning(f'(salt) cheapest = fastest, poped paths: {paths})')
                return [paths[0], cheapest, *paths[1:]]
            else:
                return paths
        elif cheapest_ind > fastest_ind:
            paths.pop(cheapest_ind)
            paths.pop(fastest_ind)
            logger.warning(f'(salt) cheapest > fastest, poped paths: {paths})')
            if fastest_ind > 0:
                return [paths[0], cheapest, fastest, *paths[1:]]
            else:
                return [fastest, cheapest, *paths]
        else:
            paths.pop(fastest_ind)
            paths.pop(cheapest_ind)
            logger.warning(f'(salt) cheapest < fastest, poped paths: {paths})')
            if cheapest_ind > 0:
                return [paths[0], cheapest, fastest, *paths[1:]]
            else:
                return [cheapest, fastest, *paths]

    def get_path_conclusion(self):
        paths = PathService.paths(self.source, self.destination, self.source_type, self.destination_type)
        for path in paths:
            PathService.calculate(path, self.good, self.special)

        paths = self.sort_paths(paths)
        logger.warning(f'(salt) after all sorts paths: {paths})')
        return PathConclusion(source=self.source, destination=self.destination, paths=paths)
