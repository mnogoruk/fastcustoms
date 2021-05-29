import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from geo.models import City
from goods.models import Good
from .models import HubRoute, Path
from .service.calculate import PathService
from .serializers import HubRouteCreateSerializer, PathConclusionSerializer, PathSerializer
from .service.models import PathConclusion


class PathView(APIView):

    def get(self, request: Request, *args, **kwargs):
        start = datetime.datetime.now()
        city1_id = request.query_params['city1']
        city2_id = request.query_params['city2']

        test_good = Good(total_volume=1, total_ldm=1, total_mass=1)

        city1 = City.objects.select_related(
            'state__country__zone',
        ).get(id=city1_id)
        city2 = City.objects.select_related(
            'state__country__zone',
        ).get(id=city2_id)

        paths = PathService.paths(city1, city2)

        for path in paths:
            PathService.calculate(path, test_good)

        serializer = PathConclusionSerializer(PathConclusion(source=city1, destination=city2, paths=paths))
        data = serializer.data
        print(datetime.datetime.now() - start)
        return Response(data=data)


class RouteViewSet(ModelViewSet):
    queryset = HubRoute.objects.all()
    serializer_class = HubRouteCreateSerializer

    def get_object(self):
        obj = super().get_object()
        return obj


class PathViewSet(ModelViewSet):
    queryset = Path.objects.all()
    serializer_class = PathSerializer


class TestView(APIView):

    def get(self, request, **kwargs):
        from django.db import connection

        # with connection.cursor() as cursor:
        #     cursor.execute()
        #     rows = cursor.fetchall()
        #     print(to_routes(rows))

        return Response(data=[])
