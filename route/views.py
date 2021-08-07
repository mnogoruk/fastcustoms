from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import HubRoute, Path
from .serializers import HubRouteSerializer, PathConclusionSerializer, PathSerializer, PathToCalculateSerializer
from .service.path import PathCalculator


class PathView(APIView):

    def post(self, request: Request, *args, **kwargs):
        serializer = PathToCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        path_calculator = PathCalculator(**serializer.validated_data)

        serializer = PathConclusionSerializer(path_calculator.get_path_conclusion())
        return Response(data=serializer.data)


class RouteViewSet(ModelViewSet):
    queryset = HubRoute.objects.all()
    serializer_class = HubRouteSerializer
    http_method_names = ['get', 'head', 'options']

    def get_object(self):
        obj = super().get_object()
        return obj


class PathViewSet(ModelViewSet):
    queryset = Path.objects.all()
    serializer_class = PathSerializer
    http_method_names = ['get', 'head', 'options']
