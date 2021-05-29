ROUTES_VIA_WAYPOINT_ZONE_QUERY = """
SELECT routes1.id, routes2.id
FROM (
    SELECT hr.id, hr.destination_id
    FROM route_hubroute hr
    INNER JOIN geo_city c ON hr.source_id = c.id
    INNER JOIN geo_state s ON c.state_id = s.id
    INNER JOIN geo_country cn ON s.country_id = cn.id
    INNER JOIN geo_zone z ON cn.zone_id = z.id
    WHERE z.id = %s
    ) routes1
INNER JOIN (
    SELECT hr.id, hr.source_id
    FROM route_hubroute hr
    INNER JOIN geo_city c ON hr.destination_id = c.id
    INNER JOIN geo_state s ON c.state_id = s.id
    INNER JOIN geo_country cn ON s.country_id = cn.id
    INNER JOIN geo_zone z ON cn.zone_id = z.id
    WHERE z.id = %s
) routes2
ON (routes1.destination_id = routes2.source_id)
"""
ROUTES_VIA_WAYPOINT_COUNTRY_QUERY = """
SELECT routes1.id, routes2.id
FROM (
    SELECT hr.id, hr.destination_id
    FROM route_hubroute hr
    INNER JOIN geo_city c ON hr.source_id = c.id
    INNER JOIN geo_state s ON c.state_id = s.id
    INNER JOIN geo_country cn ON s.country_id = cn.id
    WHERE cn.id = %s
    ) routes1
INNER JOIN (
    SELECT hr.id, hr.source_id
    FROM route_hubroute hr
    INNER JOIN geo_city c ON hr.destination_id = c.id
    INNER JOIN geo_state s ON c.state_id = s.id
    INNER JOIN geo_country cn ON s.country_id = cn.id
    WHERE cn.id = %s
) routes2
ON (routes1.destination_id = routes2.source_id)
"""

