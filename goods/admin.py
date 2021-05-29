from django.contrib import admin

from .models import Good, Container, Box
# Register your models here.

admin.site.register(Box)
admin.site.register(Good)
admin.site.register(Container)