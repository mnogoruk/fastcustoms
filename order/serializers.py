from rest_framework import serializers

from goods.serializers import GoodSerializer
from order.models import OrderAgent, Order, Special
from route.serializers import PathSerializer


class OrderAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAgent
        exclude = ['id']


class SpecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Special
        exclude = ['id']


class OrderSerializer(serializers.ModelSerializer):
    agent = OrderAgentSerializer()
    path = PathSerializer()
    good = GoodSerializer()
    special = SpecialSerializer(required=False)

    class Meta:
        model = Order
        exclude = ['time_stamp']
