from django.db import transaction
from django.db.models import Manager

class GoodCreatableManager(Manager):

    def create(self, boxes_data, containers_data):
        with transaction.atomic():
            good = super(GoodCreatableManager, self).create()
            for box_data in boxes_data:
                good.boxes.create(**box_data)
            for container_data in containers_data:
                good.containers.create(**container_data)
            good.recalculate_params()
            good.save()
        return good
