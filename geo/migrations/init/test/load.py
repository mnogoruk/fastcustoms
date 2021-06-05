import json
from random import choice

from django.conf import settings
from django.db.utils import IntegrityError
from string import ascii_lowercase


def from_json(apps, schema_editor):
    print('load test data')
    Country = apps.get_model('geo', 'Country')
    State = apps.get_model('geo', 'State')
    City = apps.get_model('geo', 'City')
    with open(settings.BASE_DIR / 'geo/migrations/init/test/test_data.json', 'r', encoding='UTF-8') as file:
        countries = json.load(file)['data']

        for country_data in countries:
            print(f'load {country_data["name"]}')
            country = Country.objects.create(
                name=country_data['name'],
                slug=country_data['name'].replace(' ', '-').replace('(', '').replace(')', ''),
                iso3=country_data.get('iso3'),
                iso2=country_data.get('iso2'),
                phone_code=country_data.get('phone_code'),
            )
            for state_data in country_data['states']:
                try:
                    state = State.objects.create(
                        name=state_data['name'],
                        slug=state_data['name'].replace(' ', '-').replace('(', '').replace(')',
                                                                                           '') + '-' + country.iso2,
                        code=state_data['state_code'],
                        country=country
                    )
                except IntegrityError:
                    continue
                for city_data in state_data['cities']:
                    try:
                        city = City.objects.create(
                            name=city_data['name'],
                            slug=city_data['name'].replace(' ', '-').replace('(', '').replace(')',
                                                                                              '') + '-' + country.iso2 + '-' + state.code + '-' + ''.join(
                                [choice(ascii_lowercase) for i in range(6)]),
                            latitude=city_data['latitude'],
                            longitude=city_data['longitude'],
                            state=state
                        )
                    except IntegrityError:
                        continue
    print('loaded')