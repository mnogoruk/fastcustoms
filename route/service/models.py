from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Union
from geo.models import City
from goods.calculation import boxes_summary
from route.models import HubRoute, RouteInPath
from utils.calculation import ldm_from_size


@dataclass
class PathDuration:
    min: float  # days
    max: float  # days


@dataclass
class Path:
    total_distance: float = 0  # km
    total_duration: PathDuration = PathDuration(0, 0)  # pair in days
    total_cost: float = 0  # euro

    fastest: bool = False
    cheapest: bool = False

    routes: List[Union[HubRoute, RouteInPath]] = field(default_factory=list)

    def __eq__(self, other: 'Path'):
        # simple eq
        if self.total_distance != other.total_distance:
            return False
        if self.total_duration != other.total_duration:
            return False
        if self.total_cost != other.total_cost:
            return False
        if len(self.routes) != len(other.routes):
            return False
        return True


@dataclass
class PathConclusion:
    source: City
    destination: City

    paths: List[Path] = field(default_factory=list)


@dataclass
class Box:
    length: float  # meters
    width: float  # meters
    height: float  # meters

    mass: float  # kg
    amount: int
    type: str

    @property
    def volume(self):
        return self.length * self.width * self.height

    @property
    def ldm(self):
        return ldm_from_size(length=self.length, width=self.width, height=self.height)


@dataclass
class Container:
    type: str
    amount: int


@dataclass
class Good:
    boxes: List[Box]
    containers: List[Container]

    total_volume: float = 0  # meters codes
    total_ldm: float = 0  # ldm
    total_mass: float = 0  # kg

    def recalculate_params(self):
        params = boxes_summary(self.boxes)
        self.total_volume = params[0]
        self.total_ldm = params[1]
        self.total_mass = params[2]

    def add_box(self, box):
        self.boxes.append(box)
        self.recalculate_params()


@dataclass
class Special:
    departure_date: datetime.date = None
