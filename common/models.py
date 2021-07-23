from django.db import models


# Create your models here.

class Customs(models.Model):
    text = models.TextField(max_length=1200)

    @classmethod
    def get(cls):
        return cls.objects.first()
