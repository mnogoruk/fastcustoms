import logging
from threading import Thread

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

email_html_template = get_template('email_order.html')
email_text_template = get_template('order_email.txt')
email_admin_html_template = get_template('email_order_admin.html')
email_admin_text_template = get_template('email_order_admin.txt')

logger = logging.getLogger('order.email')


class EmailThread(Thread):
    def __init__(self, subject, context, recipient_list, send_client=True):
        self.subject = subject
        self.recipient_list = recipient_list
        self.context = context
        self.send_client = send_client
        Thread.__init__(self)

    def run(self):
        try:
            html_email_content = email_html_template.render(self.context)
            text_email_content = email_text_template.render(self.context)
            html_email_admin_content = email_admin_html_template.render(self.context)
            text_email_admin_content = email_admin_text_template.render(self.context)
        except Exception as ex:
            logger.error(f'Error while render email template:\n{ex}')
            raise ex

        email = EmailMultiAlternatives('Заказ на Formatlogistic', text_email_content,
                                       from_email=f'Formatlogistic <{settings.DEFAULT_FROM_EMAIL}>')
        email.attach_alternative(html_email_content, "text/html")
        email.to = self.recipient_list

        email_admin = EmailMultiAlternatives('Новый заказ на Formatlogistic', text_email_admin_content,
                                             from_email=f'Formatlogistic <{settings.DEFAULT_FROM_EMAIL}>')
        email_admin.attach_alternative(html_email_admin_content, 'text/html')
        email_admin.to = [f'{settings.DEFAULT_ADMIN_EMAIL_RECIPIENT}']

        try:
            email_admin.send()
            logger.info(f"Email send success {settings.DEFAULT_ADMIN_EMAIL_RECIPIENT}")
        except Exception as ex:
            logger.error(f'Error while sending email to {settings.DEFAULT_ADMIN_EMAIL_RECIPIENT}:\n{ex}')
            raise ex

        if self.send_client:
            try:
                email.send()
                logger.info(f"Email send success {self.recipient_list}")
            except Exception as ex:
                logger.error(f'Error while sending email to {self.recipient_list}:\n{ex}')
                raise ex


def send_order_email(subject, context, recipient_list, send_client=True):
    EmailThread(subject, context, recipient_list, send_client).start()
