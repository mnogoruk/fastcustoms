from utils.enums import RouteType, PlaceType


def circle_search(array: list, index_from: int = 0, search_value=1):
    try:
        ind = array.index(search_value, index_from)
        return ind - index_from
    except ValueError:
        try:
            ind = array.index(search_value, 0, index_from + 1)
        except ValueError:
            return 0
        return len(array) - index_from + ind


def place_type_related_to_route_type(r_type):
    if r_type == RouteType.AIR.value:
        p_type = PlaceType.AIRPORT
    elif r_type == RouteType.TRAIN.value:
        p_type = PlaceType.RAILWAY_STATION
    elif r_type == RouteType.TRUCK.value:
        p_type = PlaceType.CITY
    else:
        p_type = PlaceType.default()

    return p_type
