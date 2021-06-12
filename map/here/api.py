import json
import sys
from typing import Union, List, Optional, Dict

import requests
from django.conf import settings
from herepy import RoutingApi, MatrixRoutingProfile, MatrixSummaryAttribute, MatrixRoutingType, MatrixRoutingMode, \
    MatrixRoutingTransportMode, Avoid, Truck, RoutingMatrixResponse, Utils, HEREError

from geo.models import City, Location
from map.abstract import AbstractMapAPI
from pyjavaproperties import Properties

from utils.oauth.auth import SimpleOAuth


class MapAPI(RoutingApi, AbstractMapAPI):

    def __init__(self, *args, **kwargs):
        config = Properties()
        config.load(open(settings.BASE_DIR / 'map/here/credentials.properties'))

        client_id = config['here.access.key.id']
        secret = config['here.access.key.secret']
        auth_url = config['here.token.endpoint.url']

        self.authenticator = SimpleOAuth(client_id, secret, auth_url)

        super().__init__()

    def distance_duration(self, sources: List[Union[City, Location]],
                          destinations: List[Union[City, Location]]) -> list:

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

        response = self.sync_matrix(
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

        return [(distances[i], durations[i], errors[i]) for i in range(routes_count)]

    def sync_matrix(
            self,
            origins: List[Union[List[float], str]],
            destinations: List[Union[List[float], str]],
            matrix_type: MatrixRoutingType = MatrixRoutingType.world,
            center: Optional[List[float]] = None,
            radius: Optional[int] = None,
            profile: Optional[MatrixRoutingProfile] = None,
            departure: str = None,
            routing_mode: Optional[MatrixRoutingMode] = None,
            transport_mode: Optional[MatrixRoutingTransportMode] = None,
            avoid: Optional[Avoid] = None,
            truck: Optional[Truck] = None,
            matrix_attributes: Optional[List[MatrixSummaryAttribute]] = None,
    ) -> Optional[RoutingMatrixResponse]:

        query_params = {
            "async": "false",
        }

        request_body = self.__prepare_matrix_request_body(
            origins=origins,
            destinations=destinations,
            matrix_type=matrix_type,
            center=center,
            radius=radius,
            profile=profile,
            departure=departure,
            routing_mode=routing_mode,
            transport_mode=transport_mode,
            avoid=avoid,
            truck=truck,
            matrix_attributes=matrix_attributes,
        )

        url = Utils.build_url(self.URL_CALCULATE_MATRIX, extra_params=query_params)
        headers = {"Content-Type": "application/json"}

        response = self.post(
            url, json=request_body, headers=headers, timeout=self._timeout
        )
        json_data = json.loads(response.content.decode("utf8"))
        if json_data.get("matrix") is not None:
            return RoutingMatrixResponse.new_from_jsondict(json_data)
        else:
            raise HEREError("Error in sync_ matrix")

    def post(self, url, **kwargs):
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {self.authenticator.access_token}"
        kwargs['headers'] = headers

        response = requests.post(url, **kwargs)
        if response.status_code == 401:
            self.authenticator.refresh_token()
            headers['Authorization'] = f'Bearer {self.authenticator.access_token}'
            return requests.post(url, **kwargs)
        else:
            return response

    def __prepare_matrix_request_body(
            self,
            origins: List[Union[List[float], str]],
            destinations: List[Union[List[float], str]],
            matrix_type: MatrixRoutingType = MatrixRoutingType.world,
            center: Optional[List[float]] = None,
            radius: Optional[int] = None,
            profile: Optional[MatrixRoutingProfile] = None,
            departure: str = None,
            routing_mode: Optional[MatrixRoutingMode] = None,
            transport_mode: Optional[MatrixRoutingTransportMode] = None,
            avoid: Optional[Avoid] = None,
            truck: Optional[Truck] = None,
            matrix_attributes: Optional[List[MatrixSummaryAttribute]] = None,
    ) -> Dict:
        region_definition = {
            "type": matrix_type.__str__(),
        }
        if center:
            region_definition["center"] = {"lat": center[0], "lng": center[1]}
        if radius:
            region_definition["radius"] = radius
        request_body = {
            "regionDefinition": region_definition
        }

        if profile:
            request_body["profile"] = profile.__str__()
        if departure:
            request_body["departureTime"] = departure
        if routing_mode:
            request_body["routingMode"] = routing_mode.__str__()
        if transport_mode:
            request_body["transportMode"] = transport_mode.__str__()
        if matrix_attributes:
            request_body["matrixAttributes"] = [
                attribute.__str__() for attribute in matrix_attributes
            ]
        if avoid:
            request_body["avoid"] = {"features": avoid.features, "areas": avoid.areas}
        if truck:
            request_body["truck"] = {
                "shippedHazardousGoods": truck.shipped_hazardous_goods,
                "grossWeight": truck.gross_weight,
                "weightPerAxle": truck.weight_per_axle,
                "height": truck.height,
                "width": truck.width,
                "length": truck.length,
                "tunnelCategory": truck.tunnel_category,
                "axleCount": truck.axle_count,
                "type": truck.truck_type,
                "trailerCount": truck.trailer_count,
            }

        origin_list = []
        for i, origin in enumerate(origins):
            if isinstance(origin, str):
                origin_waypoint = self._get_coordinates_for_location_name(origin)
            else:
                origin_waypoint = origin
            lat_long = {"lat": origin_waypoint[0], "lng": origin_waypoint[1]}
            origin_list.append(lat_long)
        request_body["origins"] = origin_list

        destination_list = []
        for i, destination in enumerate(destinations):
            if isinstance(destination, str):
                destination_waypoint = self._get_coordinates_for_location_name(
                    destination
                )
            else:
                destination_waypoint = destination
            lat_long = {"lat": destination_waypoint[0], "lng": destination_waypoint[1]}
            destination_list.append(lat_long)
        request_body["destinations"] = destination_list

        return request_body
