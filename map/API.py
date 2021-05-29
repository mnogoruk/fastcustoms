from typing import Union, List

from geo.models import City, Location
from map.abstract import AbstractMapAPI

from herepy import (
    RoutingApi,
    MatrixSummaryAttribute,
    MatrixRoutingProfile,
)


class MapAPI(AbstractMapAPI):
    routing_api = RoutingApi('ve_KGVZlFTz7S7wc2HsFJtWMNGN-7WeEpO4cMlIXkeI')

    @classmethod
    def distance_duration(cls, sources: List[Union[City, Location]], destinations: List[Union[City, Location]]) -> list:

        origins = []
        end_points = []

        for source in sources:
            if isinstance(source, City):
                location = source.location
            elif isinstance(source, Location):
                location = source
            else:
                raise TypeError(f"source must be instance of (City, Location). Got {type(source)}")
            origins.append([location.latitude, location.longitude])

        for destination in destinations:
            if isinstance(destination, City):
                location = destination.location
            elif isinstance(destination, Location):
                location = destination
            else:
                raise TypeError(f"destination must be instance of (City, Location). Got {type(destination)}")
            end_points.append([location.latitude, location.longitude])

        response = cls.routing_api.sync_matrix(
            origins=origins,
            destinations=end_points,
            profile=MatrixRoutingProfile.truck_fast,
            matrix_attributes=[MatrixSummaryAttribute.travel_times, MatrixSummaryAttribute.distances]
        )
        data = response.as_dict()

        routes_count = data['matrix']['numOrigins'] * data['matrix']['numDestinations']

        distances = data['matrix']['distances']
        durations = data['matrix']['travelTimes']
        errors = data['matrix'].get('errorCodes')

        if errors is None:
            errors = [0 for i in range(routes_count)]

        return [[distances[i], durations[i], errors[i]] for i in range(routes_count)]
