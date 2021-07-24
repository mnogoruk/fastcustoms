from rest_framework import serializers

from common.models import Customs


class CustomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customs
        fields = ['text']