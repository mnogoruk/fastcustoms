from collections import OrderedDict

from rest_framework import serializers


class PureLookUpFiled(serializers.Field):

    def __init__(self, original_filed: serializers.Field, lookup_fields=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if lookup_fields is None:
            lookup_fields = ['id']
        self.original_field = original_filed
        self.__lookup_fields = lookup_fields

    def to_internal_value(self, data):
        ret = OrderedDict()

        intersected_fields = []
        for lookup_field in self.__lookup_fields:
            if lookup_field in data:
                intersected_fields.append(lookup_field)

        assert len(intersected_fields) > 0, "No intersections between lookup fields and input data fields"
        for filed in intersected_fields:
            ret[filed] = data[filed]
        print(ret)
        return ret

    def to_representation(self, value):
        return self.original_field.to_representation(value)
