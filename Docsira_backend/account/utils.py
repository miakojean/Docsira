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

def generate_temporary_password():
    alphabet = string.ascii_letters + string.digits + '-_'
    return ''.join(secrets.choice(alphabet) for _ in range(14))


def send_invitation_email(user, temporary_password):

    subject = 'Vos identifiants Docsira'

    context = {
        'user': user,
        'temporary_password': temporary_password,
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


def get_invitations_data(main_account):
    from .models import CollaboratorInvitation
    inv_data = []
    invitations = CollaboratorInvitation.objects.filter(
        main_account=main_account, 
        accepted_at__isnull=True
    ).select_related('user')
    for i in invitations:
        inv_data.append({
            'id': str(i.id),
            'main_account': str(i.main_account_id),
            'role': i.role,
            'user': {
                'id': str(i.user.id),
                'username': i.user.username,
                'email': i.user.email
            },
            'status': 'pending',
            'created_at': i.created_at.isoformat() if i.created_at else None
        })
    return inv_data


def get_owner_data(main_account):
    return {
        'id': f"main_{main_account.id}",
        'main_account': str(main_account.id),
        'role': 'admin',
        'user': {
            'id': str(main_account.id),
            'username': main_account.username,
            'email': main_account.email
        },
        'status': 'accepted',
        'created_at': main_account.date_joined.isoformat() if main_account.date_joined else None
    }