from django.contrib import admin

from .models import *

admin.site.register(HubRoute)
admin.site.register(Path)
admin.site.register(RouteTimeTable)