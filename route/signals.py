from utils.functions import place_type_related_to_route_type


def correct_city_types_after_removing_hub_route(sender, instance, using, **kwargs):
    route = instance

    src_counts = sender.objects.src_count_by_type(source=route.source, r_type=route.type)
    dst_counts = sender.objects.dst_count_by_type(dest=route.destination, r_type=route.type)

    p_type_s = place_type_related_to_route_type(route.type, 's')
    p_type_d = place_type_related_to_route_type(route.type, 'd')

    if src_counts <= 1:
        route.source.exclude_type(p_type_s)
        route.source.save()

    if dst_counts <= 1:
        route.destination.exclude_type(p_type_d)
        route.destination.save()

