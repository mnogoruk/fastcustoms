import logging
from threading import Thread

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

email_html_template = get_template('email_order.html')
email_text_template = get_template('order_email.txt')

logger = logging.getLogger('order.email')


class EmailThread(Thread):
    def __init__(self, subject, context, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.context = context
        Thread.__init__(self)

    def run(self):
        try:
            html_email_content = email_html_template.render(self.context)
            text_email_content = email_text_template.render(self.context)
        except Exception as ex:
            logger.error(f'Error while render email template:\n{ex}')
            raise ex

        email = EmailMultiAlternatives('Заказ на Formatlogistic', text_email_content)
        email.attach_alternative(html_email_content, "text/html")
        email.to = self.recipient_list
        try:
            email.send()
            logger.info(f"Email send success {self.recipient_list}")
        except Exception as ex:
            logger.error(f'Error while sending email to {self.recipient_list}:\n{ex}')


def send_order_email(subject, context, recipient_list):
    EmailThread(subject, context, recipient_list).start()
