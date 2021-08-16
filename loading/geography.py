import logging

from django.db import transaction

from geo.models import City, Country, State, Zone
import json
import pandas as pd

logger = logging.getLogger('loading')


def serialize_city(city: City):
    city_dict = {'name': city.name,
                 'slug': city.slug,
                 'latitude': city.latitude,
                 'longitude': city.longitude,
                 'alias_ru': city.alias_ru}

    return city_dict


def serialize_state(state: State):
    state_dict = {'name': state.name,
                  'slug': state.slug,
                  'code': state.code,
                  'alias_en': state.alias_en,
                  'alias_ru': state.alias_ru}

    return state_dict


def serialize_country(country: Country):
    country_dict = {'name': country.name,
                    'slug': country.slug,
                    'iso2': country.iso2,
                    'iso3': country.iso3,
                    'alias_ru': country.alias_ru,
                    'alias_en': country.alias_en}

    return country_dict


def serialize(countries):
    data = []
    for country in countries:
        country_d = serialize_country(country)
        states = []
        for state in country.states.all():
            state_d = serialize_state(state)
            cities = []
            for city in state.cities.all():
                city_d = serialize_city(city)
                cities.append(city_d)
            state_d['cities'] = cities
            states.append(state_d)
        country_d['states'] = states
        data.append(country_d)
    return data


def dump_all(filename):
    countries = Country.objects.all()
    data = serialize(countries)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def load_all(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        logger.debug("START LOADING GEO")
        c_count = 0
        with transaction.atomic():
            for country_data in data:
                states = country_data.pop('states')
                c_count += 1
                logger.debug(f"load {country_data['name']} | {c_count}")
                country = Country.objects.create(**country_data)
                if len(states) > 0:
                    for state_data in states:
                        cities = state_data.pop('cities')
                        state = State.objects.create(**state_data, country=country)
                        if len(cities) > 0:
                            for city_data in cities:
                                city = City.objects.create(**city_data, state=state)


def states_to_csv():
    data = []
    for country in Country.objects.prefetch_related('states').all():
        for state in country.states.all():
            data.append([country.alias_ru, state.name])
    df = pd.DataFrame(data, columns=['Country', 'state'])
    df.to_csv('states.csv', encoding='utf-8')


def associate_zones_to_countries():
    for country in Country.objects.all():
        if country.states.count() > 0:
            zone = Zone.objects.create(name=country.name, slug=country.slug)
            zone.associate_with_country(country)
            zone.save()
