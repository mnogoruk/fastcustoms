from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Union
from geo.models import City
from goods.calculation import boxes_summary
from route.models import HubRoute, AuxiliaryRoute
from utils.calculation import ldm_from_size


@dataclass
class PathDuration:
    min: int
    max: int


@dataclass
class Path:
    total_distance: int = 0  # meters
    total_duration: PathDuration = PathDuration(0, 0)  # minutes
    total_cost: float = 0  # euro

    routes: List[Union[HubRoute, AuxiliaryRoute]] = field(default_factory=list)


@dataclass
class PathConclusion:
    source: City
    destination: City

    paths: List[Path] = field(default_factory=list)


@dataclass
class Box:
    length: float
    width: float
    height: float

    mass: float
    amount: int
    type: str

    @property
    def volume(self):
        return self.length * self.width * self.height * self.amount

    @property
    def ldm(self):
        return ldm_from_size(length=self.length, width=self.width, height=self.height) * self.amount


@dataclass
class Container:
    type: str
    amount: int


@dataclass
class Good:
    boxes: List[Box]
    containers: List[Container]

    total_volume: float = 0
    total_ldm: float = 0
    total_mass: float = 0

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
