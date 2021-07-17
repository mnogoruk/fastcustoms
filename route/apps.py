from django.apps import AppConfig
from django.db.models.signals import pre_delete

from route.signals import correct_city_types_after_removing_hub_route


class RouteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'route'

    def ready(self):
        HubRoute = self.get_model('HubRoute')
        pre_delete.connect(correct_city_types_after_removing_hub_route, sender=HubRoute)
