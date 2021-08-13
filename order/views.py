import base64
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from order.models import Order
from order.serializers import OrderSerializer
from django.template.loader import render_to_string
from django.core.mail import send_mail

from utils.enums import RouteType


def get_attachment(file_path, cid):
    with open(file_path, 'rb') as f:
        data = f.read()
        f.close()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('image/jpg')
    attachment.file_name = FileName(cid)
    attachment.disposition = Disposition('inline')
    attachment.content_id = ContentId(cid)
    return attachment


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
            message = Mail(
                from_email='lionless072@gmail.com',
                to_emails=mail_to,
                subject='Расчёт заказа Formatlogistic',
                html_content=render_to_string('order_email.html', context={'path': path, 'good': good}))
            att_unique = []
            for route in path['routes']:
                tp = route['type']
                if tp not in att_unique:
                    if tp == RouteType.TRUCK.value:
                        file_name, cid = settings.BASE_DIR / 'order/images/truck.jpg', 'truck.jpg'
                    elif tp == RouteType.TRAIN.value:
                        file_name, cid = settings.BASE_DIR / 'order/images/train.jpg', 'train.jpg'
                    elif tp == RouteType.SEA.value:
                        file_name, cid = settings.BASE_DIR / 'order/mages/ship.jpg', 'ship.jpg'
                    elif tp == RouteType.AIR.value:
                        file_name, cid = settings.BASE_DIR / 'order/images/airplane.jpg', 'airplane.jpg'
                    else:
                        file_name, cid = settings.BASE_DIR / 'order/images/truck.jpg', 'truck.jpg'
                    message.add_attachment(get_attachment(file_name, cid))
                    att_unique.append(tp)
            try:
                sg = SendGridAPIClient('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')
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)
                raise e
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
