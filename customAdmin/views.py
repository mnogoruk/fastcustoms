
from rest_framework.viewsets import ModelViewSet

from customAdmin.serializers import HubRouteCreateUpdateAdminSerializer
from route.models import HubRoute
from utils.views.mixins import FullnessMixin
from route.serializers import HubRouteShortSerializer


class RouteView(ModelViewSet, FullnessMixin):
    serializer_class = HubRouteCreateUpdateAdminSerializer
    queryset = HubRoute.objects.all()

    def get_queryset(self):
        fullness = self.fullness()
        if fullness == self.FullnessMode.FULL:
            return super().get_queryset().select_related('source', 'destination', 'timetable')
        if fullness == self.FullnessMode.SHORT:
            return super().get_queryset().select_related('source', 'destination')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HubRouteCreateUpdateAdminSerializer
        fullness = self.fullness()
        if fullness == self.FullnessMode.FULL:
            return HubRouteCreateUpdateAdminSerializer
        else:
            return HubRouteShortSerializer
