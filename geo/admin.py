from django.contrib import admin

# Register your models here.
from geo.models import City, Country, State

admin.site.register(City)
admin.site.register(Country)
admin.site.register(State)
