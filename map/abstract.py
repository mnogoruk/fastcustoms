from abc import ABC, abstractmethod
from typing import Union
from geo.models import City, Location


class AbstractMapAPI(ABC):

    @classmethod
    @abstractmethod
    def distance_duration(cls, sources: Union[City, Location], destinations: Union[City, Location]) -> dict:
        pass
