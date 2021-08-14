from django.core import mail
from django.core.mail import EmailMultiAlternatives
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.template.loader import get_template
from django.template import Context

from order.models import Order
from order.serializers import OrderSerializer

email_html_template = get_template('email_oreder.html')
email_text_template = get_template('order_email.txt')


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    http_method_names = ['post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if serializer.data['special']['send_mail']:
            mail_to = serializer.data['agent']['email']
            path = serializer.data['path']
            good = serializer.data['good']
            context = {'good': good, 'path': path}
            html_email_content = email_html_template.render(context)
            text_email_content = email_text_template.render(context)
            email = EmailMultiAlternatives('Заказ на Formatlogistic', text_email_content)
            email.attach_alternative(html_email_content, "text/html")
            email.to = [mail_to]
            response = email.send()
            print(response)
            print(email)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
