from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from order.email.multithread import send_order_email
from order.models import Order
from order.serializers import OrderSerializer


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
            send_order_email('Заказ на Formatlogistic', context, [mail_to])

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
