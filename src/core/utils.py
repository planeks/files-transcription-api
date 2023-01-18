from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string


def send_html_email(subject, to, html_template_name, txt_template_name, context=None):
    if not context:
        context = {}
    html_message = render_to_string(html_template_name, context)
    plain_message = render_to_string(txt_template_name, context)
    mail.send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, to, html_message=html_message)
