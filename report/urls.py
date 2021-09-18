from django.urls import path

from report.views import PDFHandlerView

urlpatterns = [
    path('report', PDFHandlerView.as_view())
]
