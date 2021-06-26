from rest_framework.routers import SimpleRouter

from geo.views import CityViewSet, StateViewSet, CountryViewSet, ZoneViewSet

router = SimpleRouter()

router.register('cities', CityViewSet)
router.register('states', StateViewSet)
router.register('countries', CountryViewSet)
router.register('zones', ZoneViewSet)

urlpatterns = router.urls
