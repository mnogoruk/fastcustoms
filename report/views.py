from django.shortcuts import render
from rest_framework import status
from drf_pdf.response import PDFResponse
from drf_pdf.renderer import PDFRenderer
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from report.serializer import ReportInputSerializer
from django.template.loader import get_template
from weasyprint import HTML

from route.service.models import Good, Box


def generate_extra_msg(route):
    route['description'] = route['description'].split('\n\n')
    return route


def generate_report(data, base_url):
    volume = 0
    mass = 0
    for box in data['good']['boxes']:
        box = Box(**box)
        volume += box.volume * box.amount
        mass += box.mass * box.amount

    context = {
        'path': data['path'],
        'customs': data['customs'],
        'good': {'total_mass': mass, 'total_volume': volume},
    }
    extra = list(filter(lambda route: route['is_hub'] and route.get('description', None), data['path']['routes']))
    extra = map(generate_extra_msg, extra)
    context['extra'] = {'routes': extra}
    rendered_html = get_template('report.html').render(context)
    return HTML(string=rendered_html, base_url=base_url).write_pdf()


class PDFHandlerView(APIView):
    renderer_classes = (PDFRenderer, JSONRenderer, BrowsableAPIRenderer)
    get_serializer = ReportInputSerializer

    def get(self, request):
        return Response(status=status.HTTP_200_OK, data={'d': 1})

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pdf = generate_report(serializer.validated_data, request.build_absolute_uri())

        return PDFResponse(
            pdf=pdf,
            file_name='report.pdf',
            status=status.HTTP_200_OK
        )
