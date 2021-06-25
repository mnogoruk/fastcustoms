from rest_framework import routers

from .views import RouteView
urlpatterns = []

router = routers.DefaultRouter()
router.register('routes', RouteView)
urlpatterns += router.urls