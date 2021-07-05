from geo.models import City
from order.models import Special
from route.service.calculate import PathService
from route.service.models import PathConclusion, Box, Container, Good


class PathCalculator:

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
            'state__country__zone',
        ).get(id=place_id)

    def __init__(self, **data):
        self.source = self.get_place(data.pop('source', {}).pop('id'))
        self.destination = self.get_place(data.pop('destination', {}).pop('id'))
        self.good = self.built_good(good_data=data.pop('good', {}))
        self.special = self.build_special(special_data=data.pop('special', {}))

    def get_path_conclusion(self):
        paths = PathService.paths(self.source, self.destination)

        for path in paths:
            PathService.calculate(path, self.good, self.special)

        return PathConclusion(source=self.source, destination=self.destination, paths=paths)
