from django.db import models

from utils.calculation import ldm_from_size
from utils.enums import ContainerType, BoxType
from .calculation import boxes_summary
from .managers import GoodCreatableManager


class Good(models.Model):
    total_volume = models.FloatField(blank=True, default=0, null=True)
    total_ldm = models.FloatField(blank=True, default=0)
    total_mass = models.FloatField(blank=True, default=0)

    creatable = GoodCreatableManager()

    def recalculate_params(self):
        params = boxes_summary(self.boxes.all())
        self.total_volume = params[0]
        self.total_ldm = params[1]
        self.total_mass = params[2]

    def add_box(self, box):
        self.boxes.add(box)
        self.recalculate_params()


class Box(models.Model):
    # dimensions
    length = models.FloatField()  # meters
    width = models.FloatField()  # meters
    height = models.FloatField()  # meters

    mass = models.FloatField()  # kg
    amount = models.IntegerField()

    type = models.CharField(max_length=20, default=BoxType.BOX.value, choices=BoxType.choices())

    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='boxes')

    @property
    def volume(self):
        # meters cubes
        return self.length * self.width * self.height * self.amount

    @property
    def ldm(self):
        # ldm
        return ldm_from_size(length=self.length, width=self.width, height=self.height) * self.amount


class Container(models.Model):
    type = models.CharField(max_length=40, default=ContainerType.SMALL.value, choices=ContainerType.choices())
    amount = models.IntegerField()

    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='containers')
