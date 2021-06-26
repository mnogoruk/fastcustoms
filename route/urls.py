from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import RouteViewSet, PathView

router = SimpleRouter()
router.register('routes', RouteViewSet)

urlpatterns = router.urls
urlpatterns.append(
    path('paths', PathView.as_view())
)