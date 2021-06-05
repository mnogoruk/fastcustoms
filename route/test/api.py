from typing import Union, List

from geo.models import City, Location
from map.abstract import AbstractMapAPI


class TestMapAPI(AbstractMapAPI):
    DEFAULT_DISTANCE = 700000
    DEFAULT_DURATION = 6000

    @classmethod
    def distance_duration(cls, sources: List[Union[City, Location]], destinations: List[Union[City, Location]]) -> list:
        return [(cls.DEFAULT_DISTANCE, cls.DEFAULT_DURATION, 0) for _ in range(len(sources) * len(destinations))]
