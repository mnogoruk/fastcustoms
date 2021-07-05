from rest_framework import serializers

from goods.models import Good
from goods.serializers import GoodSerializer
from order.models import OrderUnit, Order, Special
from route.models import Path
from route.serializers import PathSerializer


class OrderUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderUnit
        exclude = ['id']


class SpecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Special
        exclude = ['id']


class OrderSerializer(serializers.ModelSerializer):
    shipper = OrderUnitSerializer()
    consignee = OrderUnitSerializer()
    path = PathSerializer()
    good = GoodSerializer()
    special = SpecialSerializer(required=False)

    def create(self, validated_data):
        print(validated_data)
        shipper = OrderUnit.objects.create(**validated_data.pop('shipper'))
        consignee = OrderUnit.objects.create(**validated_data.pop('consignee'))
        path = Path.creatable.create(**validated_data.pop('path'))
        good = Good.creatable.create(**validated_data.pop('good'))
        if 'special' in validated_data:
            special = Special.objects.create(**validated_data.pop('special'))
        else:
            special = Special.objects.create()
        return Order.objects.create(shipper=shipper, consignee=consignee, path=path, good=good, special=special)

    class Meta:
        model = Order
        exclude = ['id','time_stamp', ]
