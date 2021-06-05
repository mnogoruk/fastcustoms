import json


def migrate():
    data = []
    test_countries = ['Russia', 'Poland', 'Germany', 'France']
    with open('../countriesStateCity.json', 'r', encoding='UTF-8') as file:
        countries = json.load(file)['data']
        for country in countries:
            if country['name'] in test_countries:
                test_countries.pop(test_countries.index(country['name']))
                data.append(country)
            if len(test_countries) == 0:
                break
    with open('./test_data.json', 'w', encoding='UTF-8') as file:
        writable = {"data": data}
        json.dump(writable, file)


migrate()
