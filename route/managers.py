from django.db.models import Manager

from geo.models import Zone, Country


class HubRouteManager(Manager):

    def find_by_zone(self, source: Zone, dest: Zone):
        return self.filter(
            source__state__country__zone__id=source.id,
            destination__state__country__zone__id=dest.id
        )

    def find_by_country(self, source: Country, dest: Country):
        return self.filter(
            source__state__country=source,
            destination__state__country=dest
        )