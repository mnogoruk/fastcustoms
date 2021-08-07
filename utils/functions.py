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


def place_type_related_to_route_type(r_type, flg):
    if r_type == RouteType.AIR.value:
        if flg == 's':
            p_type = PlaceType.AIRPORT_SRC.value
        else:
            p_type = PlaceType.AIRPORT_DST.value
    elif r_type == RouteType.TRAIN.value:
        if flg == 's':
            p_type = PlaceType.RAILWAY_STATION_SRC.value
        else:
            p_type = PlaceType.RAILWAY_STATION_DST.value
    elif r_type == RouteType.TRUCK.value:
        if flg == 's':
            p_type = PlaceType.WAREHOUSE_SRC.value
        else:
            p_type = PlaceType.WAREHOUSE_DST.value
    elif r_type == RouteType.SEA.value:
        if flg == 's':
            p_type = PlaceType.SEAPORT_SRC
        else:
            p_type = PlaceType.SEAPORT_DST
    else:
        p_type = PlaceType.default().value

    return p_type
