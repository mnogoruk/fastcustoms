from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt import views as jwt_views
from django.urls import path
from .views import RouteView, ZoneViewSet, OrderViewSet, CustomsEditView

router = SimpleRouter()
router.register('admin-routes', RouteView)
router.register('admin-zones', ZoneViewSet)
router.register('admin-orders', OrderViewSet)
urlpatterns = router.urls
urlpatterns.append(
    path('auth/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair')
)
urlpatterns.append(
    path('auth/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh')
)
urlpatterns.append(
    path('customs/', CustomsEditView.as_view(), name='edit-customs')
)
