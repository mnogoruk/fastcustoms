from typing import List
from math import exp

from geo.models import City
from order.models import Special
from route.service.calculate import PathService
from route.service.models import PathConclusion, Box, Container, Good
from utils.enums import PlaceType
from .models import Path

DURATION_WEIGHT = 1
COST_WEIGHT = 1


def sort_func(path: Path, avg_cost, avg_duration):
    return exp(path.total_cost / avg_cost) * COST_WEIGHT + exp(path.total_duration.max / avg_duration) * DURATION_WEIGHT


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
        if len(paths) == 0:
            return paths

        fastest = paths[0]
        cheapest = paths[0]

        fastest_ind = 0
        cheapest_ind = 0

        # for avg
        total_cost = 0
        total_duration = 0

        for ind, path in enumerate(paths):
            if path.total_cost < cheapest.total_cost:
                cheapest = path
                cheapest_ind = ind
            if path.total_duration.max < fastest.total_duration.max:
                fastest = path
                fastest_ind = ind

            total_cost += path.total_cost
            total_duration += path.total_duration.max

        if fastest_ind == cheapest_ind:
            paths.pop(fastest_ind)
        elif fastest_ind > cheapest_ind:
            paths.pop(fastest_ind)
            paths.pop(cheapest_ind)
        else:
            paths.pop(cheapest_ind)
            paths.pop(fastest_ind)

        fastest.fastest = True
        cheapest.cheapest = True
        if len(paths) == 0:
            others = []
        else:
            avg_cost = total_cost / len(paths)
            avg_duration = total_duration / len(paths)

            others = sorted(paths, key=lambda p: sort_func(p, avg_cost, avg_duration))

        if fastest_ind == cheapest_ind:
            return [fastest, *others]
        else:
            return [fastest, cheapest, *others]

    def get_path_conclusion(self):
        paths = PathService.paths(self.source, self.destination, self.source_type, self.destination_type)
        for path in paths:
            PathService.calculate(path, self.good, self.special)

        paths = self.sort_paths(paths)

        return PathConclusion(source=self.source, destination=self.destination, paths=paths)
