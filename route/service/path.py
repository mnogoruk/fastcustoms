from geo.models import City
from order.models import Special
from route.service.calculate import PathService
from route.service.models import PathConclusion, Box, Container, Good
from utils.enums import PlaceType


class PathCalculator:

    def __init__(self, **data):
        self.source = self.get_place(data.pop('source', {}).pop('id'))
        self.destination = self.get_place(data.pop('destination', {}).pop('id'))
        self.source_type = data.pop('source_type', PlaceType.default().value)
        self.destination_type = data.pop('destination_type', PlaceType.default().value)
        self.good = self.built_good(good_data=data.pop('good', {}))
        self.special = self.build_special(special_data=data.pop('special', {}))

        print('------')
        print(self.good)
        print(self.good.boxes)
        for box in self.good.boxes:
            print('-')
            print('\tlength:', box.length)
            print('\theight:', box.height)
            print('\twidth:', box.width)
            print('\tvolume:', box.volume)
            print('\tldm:', box.ldm)
            print('\tmass:', box.mass)
            print('-')
        print('------')

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

    def get_path_conclusion(self):
        paths = PathService.paths(self.source, self.destination, self.source_type, self.destination_type)
        print('paths: ', paths)
        for path in paths:
            print('path: ', path)
            PathService.calculate(path, self.good, self.special)

        return PathConclusion(source=self.source, destination=self.destination, paths=paths)
