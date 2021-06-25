from rest_framework import routers

from .views import RouteView
urlpatterns = []

router = routers.DefaultRouter()
router.register('admin-routes', RouteView)
urlpatterns += router.urls