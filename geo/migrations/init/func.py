import json

from django.conf import settings
from django.db import transaction


def from_json(apps, schema_editor):
    Country = apps.get_model('geo', 'Country')
    State = apps.get_model('geo', 'State')
    City = apps.get_model('geo', 'City')
    with open(settings.BASE_DIR / 'geo/migrations/init/countriesStateCity.json', encoding='UTF-8') as file:
        countries = json.load(file)['data']
        with transaction.atomic():
            for country_data in countries:
                country = Country.objects.get_or_create(
                    name=country_data['name'],
                    slug=country_data['name'].replace(' ', '-').replace('(', '').replace(')', ''),
                    iso3=country_data.get('iso3'),
                    iso2=country_data.get('iso2'),
                    phone_code=country_data.get('phone_code'),
                )[0]
                for state_data in country_data['states']:
                    state = State.objects.get_or_create(
                        name=state_data['name'],
                        slug=state_data['name'].replace(' ', '-').replace('(', '').replace(')', ''),
                        code=state_data['state_code'],
                        country=country
                    )[0]
                    for city_data in state_data['cities']:
                        city = City.objects.get_or_create(
                            name=city_data['name'],
                            slug=city_data['name'].replace(' ', '-').replace('(', '').replace(')', ''),
                            latitude=city_data['latitude'],
                            longitude=city_data['longitude'],
                            state=state
                        )[0]


def set_capital(apps, schema):
    Country = apps.get_model('geo', 'Country')
    City = apps.get_model('geo', 'City')
    with open(settings.BASE_DIR / 'geo/migrations/init/countriesStateCity.json', encoding='UTF-8') as file:
        countries = json.load(file)['data']
        with transaction.atomic():
            for country_data in countries:
                country = Country.objects.get(name=country_data['name'])
                try:
                    country.capital = City.objects.get(name=country_data['capital'], state__country=country)
                except City.DoesNotExist:
                    country.capital = None
                except City.MultipleObjectsReturned:
                    print(country.name, country_data['capital'])
                country.save()
