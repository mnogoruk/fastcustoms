from rest_framework import serializers

from goods.models import Good
from goods.serializers import GoodSerializer
from order.models import OrderAgent, Order, Special
from route.models import Path
from route.serializers import PathSerializer, PathRouteCreatableSerializer


class OrderAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAgent
        exclude = ['id']


class SpecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Special
        exclude = ['id']


class PathCreatableSerializer(PathSerializer):
    routes = PathRouteCreatableSerializer(many=True)


class OrderSerializer(serializers.ModelSerializer):
    agent = OrderAgentSerializer()
    good = GoodSerializer()
    special = SpecialSerializer(required=False)
    path = PathCreatableSerializer()

    def create(self, validated_data):
        agent = OrderAgent.objects.create(**validated_data.pop('agent'))
        path = Path.creatable.create(**validated_data.pop('path'))
        good = Good.creatable.create(**validated_data.pop('good'))
        if 'special' in validated_data:
            special = Special.objects.create(**validated_data.pop('special'))
        else:
            special = Special.objects.create()

        return Order.objects.create(agent=agent, path=path, good=good, special=special, **validated_data)

    class Meta:
        model = Order
        exclude = ['time_stamp']
        read_only_fields = ['slug']
