from enum import Enum


class SelectableMixin:

    @classmethod
    def choices(cls):
        choices = [(member.name, member.value) for member in cls.__members__.values()]
        return choices

class RouteType(SelectableMixin, Enum):
    TRUCK = 'TRUCK'
    TRAIN = 'TRAIN'
    AIR = 'AIR'

    @classmethod
    def default(cls):
        return cls.TRUCK

class PlaceType(SelectableMixin, Enum):
    CITY = 'CITY'
    AIRPORT = 'AIRPORT'
    RAILWAY_STATION = 'RAILWAY_STATION'
    SEAPORT = 'SEAPORT'

    @classmethod
    def default(cls):
        return cls.CITY


class BoxType(SelectableMixin, Enum):
    BOX = 'BOX'
    PALLET = 'PALLET'

    @classmethod
    def default(cls):
        return cls.BOX


class Currency(SelectableMixin, Enum):
    DOLLAR = '$'
    EURO = 'EUR'

    @classmethod
    def default(cls):
        return cls.EURO


class ContainerType(SelectableMixin, Enum):
    SMALL = "20'"
    MIDDLE = "40'"
    BIG = "40'HC"
    LARGE = "45'HC"

    @classmethod
    def default(cls):
        return cls.SMALL


class RateType(SelectableMixin, Enum):
    MASS = 'MASS'
    SIZE = 'SIZE'
    LDM = 'LDM'

    __default__ = MASS


class MeasurementUnits(SelectableMixin, Enum):
    KILOGRAM = 'kg'
    CUBIC_METER = 'm3'
    LDM = 'ldm'


class RateUseType(SelectableMixin, Enum):
    ROUTE = 'ROUTE'
    ZONE = 'ZONE'
