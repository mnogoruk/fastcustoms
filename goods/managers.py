from django.db import transaction
from django.db.models import Manager


class GoodCreatableManager(Manager):

    def create(self, boxes=None, containers=None):
        if boxes is None:
            boxes = []
        if containers is None:
            containers = []
        with transaction.atomic():
            good = super(GoodCreatableManager, self).create()
            for box_data in boxes:
                good.boxes.create(**box_data)
            for container_data in containers:
                good.containers.create(**container_data)
            good.recalculate_params()
            good.save()
        return good
