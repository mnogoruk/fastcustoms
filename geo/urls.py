from rest_framework import routers

from geo.views import CityViewSet, StateViewSet, CountryViewSet, ZoneViewSet, CityIndexViewSet
urlpatterns = []

router = routers.SimpleRouter()

router.register('cities', CityViewSet)
router.register('states', StateViewSet)
router.register('countries', CountryViewSet)
router.register('zones', ZoneViewSet)
router.register('icites', CityIndexViewSet)

urlpatterns += router.urls
