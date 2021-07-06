from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet

from .models import HubRoute, Path
from .serializers import HubRouteSerializer, PathConclusionSerializer, PathSerializer, PathToCalculateSerializer
from .service.path import PathCalculator


class PathView(GenericAPIView):

    def post(self, request: Request, *args, **kwargs):
        serializer = PathToCalculateSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        path_calculator = PathCalculator(**serializer.validated_data)

        serializer = PathConclusionSerializer(path_calculator.get_path_conclusion())
        return Response(data=serializer.data)


class RouteViewSet(ModelViewSet):
    queryset = HubRoute.objects.all()
    serializer_class = HubRouteSerializer

    def get_object(self):
        obj = super().get_object()
        return obj


class PathViewSet(ModelViewSet):
    queryset = Path.objects.all()
    serializer_class = PathSerializer


