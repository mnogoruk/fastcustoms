from django.contrib.postgres.fields import ArrayField
from django.db import models
from geo.models import City, Zone
from map.API import MapAPI
from route.managers import HubRouteManager
from utils.enums import RouteType
from utils.db.models import AbstractCreate


class RouteTimeTable(models.Model):
    weekdays = ArrayField(
        models.IntegerField(),
        size=7,
        default=list
    )  # each element is day of week. active - 1, inactive - 0
    preparation_period = models.IntegerField(default=0)  # days


class HubRoute(AbstractCreate):
    """
    Hub route uses for price paths.
    """
    source = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hub_routes_as_source')
    destination = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hub_routes_as_destination')

    type = models.CharField(max_length=20, default=RouteType.TRUCK.value, choices=RouteType.choices())

    timetable = models.OneToOneField(RouteTimeTable, on_delete=models.SET_NULL, null=True)

    distance = models.IntegerField()
    duration = models.IntegerField()

    is_hub = True

    objects = HubRouteManager()

    def __str__(self):
        return f"{self.source} - {self.destination}"


class Path(models.Model):
    hub_routes = models.ManyToManyField(HubRoute, related_name='paths')
    total_distance = models.IntegerField(default=0)
    total_duration = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    # for auxiliary routes look at AuxiliaryRoute


class AuxiliaryRoute(AbstractCreate):
    """
    Auxiliary routes distance and duration - data taken from map API, so we can't store it.
    Auxiliary route is exact part of path.
    """

    source = models.ForeignKey(City, on_delete=models.CASCADE, related_name='auxiliary_routes_as_source')
    destination = models.ForeignKey(City, on_delete=models.CASCADE, related_name='auxiliary_routes_as_destination')

    type = models.CharField(max_length=20, default=RouteType.TRUCK.value, choices=RouteType.choices())

    path = models.ForeignKey(Path, on_delete=models.CASCADE, related_name='auxiliary_routes', null=True)

    _distance = None
    _duration = None

    is_hub = False

    @property
    def distance(self):
        if self._distance is None:
            self.update_distance_duration()
        return self._distance

    @property
    def duration(self):
        if self._duration is None:
            self.update_distance_duration()
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = value

    @distance.setter
    def distance(self, value):
        self._distance = value

    def update_distance_duration(self):
        dde = MapAPI.distance_duration([self.source], [self.destination])
        if dde[2] != 0:
            self._distance = dde[0]
            self._duration = dde[1]
        else:
            self._distance = 0
            self._duration = 0

    def __str__(self):
        return f"{self.source} - {self.destination}"
