from rest_framework.routers import SimpleRouter

from .views import RouteView, ZoneViewSet, OrderViewSet

router = SimpleRouter()
router.register('admin-routes', RouteView)
router.register('admin-zones', ZoneViewSet)
router.register('admin-orders', OrderViewSet)
urlpatterns = router.urls
