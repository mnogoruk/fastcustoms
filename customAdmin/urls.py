from rest_framework.routers import SimpleRouter

from .views import RouteView, ZoneRateView

router = SimpleRouter()
router.register('admin-routes', RouteView)
router.register('admin-zones', ZoneRateView)
urlpatterns = router.urls
