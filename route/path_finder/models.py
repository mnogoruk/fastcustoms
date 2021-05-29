from dataclasses import dataclass, field
from typing import List, Union
from geo.models import City
from route.models import HubRoute, AuxiliaryRoute


@dataclass
class Path:
    total_distance: int = 0  # meters
    total_duration: int = 0  # minutes
    total_cost: float = 0  # euro

    routes: List[Union[HubRoute, AuxiliaryRoute]] = field(default_factory=list)


@dataclass
class PathConclusion:
    source: City
    destination: City

    paths: List[Path] = field(default_factory=list)
