from rest_framework import serializers

from goods.models import Good
from goods.serializers import GoodSerializer
from order.models import OrderUnit, Order
from route.models import Path
from route.serializers import PathSerializer


class OrderUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderUnit
        exclude = ['id']


class OrderSerializer(serializers.ModelSerializer):
    shipper = OrderUnitSerializer()
    consignee = OrderUnitSerializer()
    path = PathSerializer()
    good = GoodSerializer()

    def create(self, validated_data):
        shipper = OrderUnit.objects.create(**validated_data.pop('shipper'))
        consignee = OrderUnit.objects.create(**validated_data.pop('consignee'))

        path = Path.objects.create(**validated_data.pop('path'))
        good = Good.objects.create(**validated_data.pop('good'))

        return Order.objects.create(shipper=shipper, consignee=consignee, path=path, good=good)

    class Meta:
        model = Order
        fields = '__all__'
