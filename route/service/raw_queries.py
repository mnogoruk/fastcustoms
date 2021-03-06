ROUTES_VIA_WAYPOINT_ZONE_QUERY = """
SELECT routes1.id, routes2.id
FROM (
    SELECT hr.id, hr.destination_id
    FROM route_hubroute hr
    INNER JOIN geo_city c ON hr.source_id = c.id
    INNER JOIN geo_state s ON c.state_id = s.id
    INNER JOIN geo_zone z ON s.zone_id = z.id
    WHERE z.id = %(source_id)s
    AND %(source_type)s = ANY(c.types)
    AND hr.active = true
    AND cargo_type = %(cargo_type)s
    ) routes1
INNER JOIN (
    SELECT hr.id, hr.source_id
    FROM route_hubroute hr
    INNER JOIN geo_city c ON hr.destination_id = c.id
    INNER JOIN geo_state s ON c.state_id = s.id
    INNER JOIN geo_zone z ON s.zone_id = z.id
    WHERE z.id = %(description_id)s
    AND %(description_type)s = ANY(c.types)
    AND hr.active = true
    AND cargo_type = %(cargo_type)s
) routes2

ON (routes1.destination_id = routes2.source_id)
"""
