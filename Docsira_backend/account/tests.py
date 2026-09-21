from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Collaborator, CollaboratorInvitation
from .serializers import CustomUserSerializer


class CustomUserSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            email="alice@example.com",
            first_name="Alice",
            last_name="Dupont",
            account_type="firm",
        )

    def test_update_profile_keeps_first_and_last_name(self):
        payload = {
            "first_name": "Alicia",
            "last_name": "Martin",
            "username": "alice",
            "email": "alice.updated@example.com",
            "account_type": "individual",
        }

        serializer = CustomUserSerializer(self.user, data=payload, partial=True)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, "Alicia")
        self.assertEqual(updated_user.last_name, "Martin")
        self.assertEqual(updated_user.account_type, "individual")
        self.assertEqual(updated_user.email, "alice.updated@example.com")


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            email="alice@example.com",
            password="Secret123!",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_logout_blacklists_refresh_token(self):
        refresh_token = str(RefreshToken.for_user(self.user))

        response = self.client.post(
            "/account/logout/",
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, 204)

        refresh_response = self.client.post(
            "/account/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(refresh_response.status_code, 401)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@docsira.test",
)
class CollaborateurViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            email="alice@example.com",
            password="Secret123!",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_invitation_sends_credentials_without_creating_collaborator(self):
        response = self.client.post(
            "/account/collaborators/",
            {"email": "bob@example.com", "role": "editor"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["bob@example.com"])
        self.assertIn("bob@example.com", mail.outbox[0].body)
        self.assertIn("Mot de passe", mail.outbox[0].body)
        self.assertFalse(Collaborator.objects.filter(main_account=self.user).exists())
        self.assertTrue(CollaboratorInvitation.objects.filter(main_account=self.user, role="editor").exists())

    def test_first_login_accepts_invitation_as_collaborator(self):
        invitation_response = self.client.post(
            "/account/collaborators/",
            {"email": "bob@example.com", "role": "editor"},
            format="json",
        )
        invitation = CollaboratorInvitation.objects.get(id=invitation_response.data["id"])
        password = mail.outbox[0].body.split("Mot de passe :</strong> ", 1)[1].split("<", 1)[0]

        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/account/login/",
            {"email": invitation.user.email, "password": password},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Collaborator.objects.filter(main_account=self.user, user=invitation.user, role="editor").exists())
        invitation.refresh_from_db()
        self.assertIsNotNone(invitation.accepted_at)
