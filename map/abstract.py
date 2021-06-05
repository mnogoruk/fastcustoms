from abc import ABC, abstractmethod
from typing import Union, List
from geo.models import City, Location


class AbstractMapAPI(ABC):

    @abstractmethod
    def distance_duration(self, sources: List[Union[City, Location]], destinations: List[Union[City, Location]]) -> list:
        pass
