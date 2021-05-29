from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import RouteViewSet, PathView, TestView

router = DefaultRouter()
router.register('routes', RouteViewSet)
urlpatterns = router.urls
urlpatterns.append(
    path('paths', PathView.as_view())
)
urlpatterns.append(
    path('test', TestView.as_view())
)