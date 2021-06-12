from haystack import indexes
from .models import City


class CityIndex(indexes.SearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    slug = indexes.CharField(model_attr='slug')
    id = indexes.IntegerField(model_attr='id')
    latitude = indexes.FloatField(model_attr='latitude')
    longitude = indexes.FloatField(model_attr='longitude')
    autocomplete = indexes.EdgeNgramField()

    location = indexes.LocationField(model_attr='location')

    def get_model(self):
        return City
