from rest_framework import serializers

from goods.models import Box, Container, Good


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        exclude = ['id', 'good']


class ContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Container
        exclude = ['id', 'good']


class GoodSerializer(serializers.ModelSerializer):
    boxes = BoxSerializer(many=True, required=False)
    containers = ContainerSerializer(many=True, required=False)
    total_volume = serializers.FloatField(read_only=True)
    total_ldm = serializers.FloatField(read_only=True)
    total_mass = serializers.FloatField(read_only=True)

    class Meta:
        model = Good
        exclude = ['id']
