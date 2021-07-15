from rest_framework.routers import SimpleRouter

from .views import RouteView, ZoneRateView, OrderViewSet

router = SimpleRouter()
router.register('admin-routes', RouteView)
router.register('admin-zones', ZoneRateView)
router.register('admin-orders', OrderViewSet)
urlpatterns = router.urls
