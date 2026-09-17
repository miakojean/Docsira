import secrets
import string
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.template.loader import render_to_string

def generate_activation_code(user):

    alphabet = string.ascii_letters + string.digits
    short_token = ''.join(secrets.choice(alphabet) for _ in range(6))

    expires_at = timezone.now() + timedelta(hours=1)

    from .models import ActivationCode

    ActivationCode.objects.filter(user=user).delete()
    ActivationCode.objects.create(
        user=user,
        code=short_token,
        expires_at=expires_at
    )

    return short_token

def send_activation_email(user, activation_code):

    subject = 'Activation de votre compte Docsira'

    context = {
        'user': user,
        'activation_code': activation_code,
    }

    html_content = render_to_string('activation_code.html', context)

    email = EmailMessage(
        subject,
        html_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email.content_subtype = "html"
    email.send()