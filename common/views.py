from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from common.models import Customs
from common.serializers import CustomsSerializer


class CustomView(APIView):

    def get(self, *args, **kwargs):
        serializer = CustomsSerializer(Customs.get())
        return Response(data=serializer.data)
