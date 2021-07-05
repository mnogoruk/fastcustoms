from rest_framework.routers import SimpleRouter

from order.views import OrderViewSet

router = SimpleRouter()
router.register('orders', OrderViewSet)
urlpatterns = router.urls
