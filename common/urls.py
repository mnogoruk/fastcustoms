from importlib.resources import path

from common.views import CustomView

urlpatterns = [
    path('customs/', CustomView.as_view())
]