from utils.functions import place_type_related_to_route_type


def correct_city_types_after_removing_hub_route(sender, instance, using, **kwargs):
    route = instance
    place_counts = sender.objects.places_count_by_type(source=route.source,
                                                       dest=route.destination,
                                                       r_type=route.type)
    p_type = place_type_related_to_route_type(route.type)

    if place_counts['source_count'] <= 1:
        route.source.exclude_type(p_type)
    if place_counts['destination_count'] <= 1:
        route.destination.exclude_type(p_type)
    route.source.save()
    route.destination.save()
