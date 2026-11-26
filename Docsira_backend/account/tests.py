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

    def test_update_profile_blocks_account_type_and_hashes_password(self):
        payload = {
            "first_name": "Alicia",
            "last_name": "Martin",
            "username": "alice",
            "email": "alice.updated@example.com",
            "account_type": "individual",
            "has_changed_password": True,
        }

        serializer = CustomUserSerializer(self.user, data=payload, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_user = serializer.save()

        self.assertEqual(updated_user.first_name, "Alicia")
        self.assertEqual(updated_user.last_name, "Martin")
        self.assertEqual(updated_user.account_type, "firm")
        self.assertFalse(updated_user.has_changed_password)
        self.assertEqual(updated_user.email, "alice.updated@example.com")

        # Vérifie également PUT /account/me/ avec un mot de passe (haché, jamais en clair)
        client = APIClient()
        client.force_authenticate(user=self.user)
        resp = client.put(
            "/account/me/",
            {"password": "NewStrongPassword!2026", "account_type": "collaborator"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.account_type, "firm")
        self.assertTrue(self.user.has_changed_password)
        self.assertTrue(self.user.check_password("NewStrongPassword!2026"))
        self.assertNotEqual(self.user.password, "NewStrongPassword!2026")


class AuthSecurityTests(TestCase):
    def test_anonymous_get_activation_codes_returns_401(self):
        client = APIClient()
        response = client.get("/account/collaboratos/code/")
        self.assertEqual(response.status_code, 401)

    def test_register_forces_firm_account_type(self):
        client = APIClient()
        response = client.post(
            "/account/register/",
            {
                "username": "new-firm",
                "email": "new-firm@example.com",
                "password": "StrongPassword!2026",
                "account_type": "collaborator",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        created = get_user_model().objects.get(username="new-firm")
        self.assertEqual(created.account_type, "firm")


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


class ChangePasswordViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            email="alice@example.com",
            password="OldSecret123!",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_changes_authenticated_user_password(self):
        response = self.client.post(
            "/account/change-password/",
            {
                "old_password": "OldSecret123!",
                "new_password": "NewSecret123!",
                "confirm_password": "NewSecret123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecret123!"))

    def test_rejects_incorrect_old_password(self):
        response = self.client.post(
            "/account/change-password/",
            {
                "old_password": "WrongSecret123!",
                "new_password": "NewSecret123!",
                "confirm_password": "NewSecret123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldSecret123!"))


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

    def test_collaborators_list_is_paginated(self):
        for idx in range(3):
            self.client.post(
                "/account/collaborators/",
                {"email": f"collab{idx}@example.com", "role": "viewer"},
                format="json",
            )

        page1 = self.client.get("/account/collaborators/?page=1&page_size=2")
        self.assertEqual(page1.status_code, 200)
        self.assertEqual(page1.data["count"], 3)
        self.assertEqual(len(page1.data["results"]), 2)
        self.assertIsNotNone(page1.data["next"])

        page2 = self.client.get("/account/collaborators/?page=2&page_size=2")
        self.assertEqual(page2.status_code, 200)
        self.assertEqual(len(page2.data["results"]), 1)
        self.assertIsNone(page2.data["next"])

    def test_default_role_is_editor_and_admin_can_assign_roles(self):
        # 1. Par défaut (sans précision), le rôle invité est "editor" (Collaborateur)
        inv_default = self.client.post(
            "/account/collaborators/",
            {"email": "default.collab@example.com"},
            format="json",
        )
        self.assertEqual(inv_default.status_code, 201)
        self.assertEqual(inv_default.data["role"], "editor")

        # 2. Changer le rôle d'une invitation en attente (admin / viewer / editor)
        inv_id = inv_default.data["id"]
        patch_inv = self.client.patch(
            f"/account/collaborators/{inv_id}/role/",
            {"role": "viewer"},
            format="json",
        )
        self.assertEqual(patch_inv.status_code, 200)
        self.assertEqual(patch_inv.data["role"], "viewer")

        # 3. Créer un administrateur, un collaborateur et un lecteur actifs
        admin_user = get_user_model().objects.create_user(
            username="admin-col",
            email="admin-col@example.com",
            password="Secret123!",
            account_type="collaborator",
        )
        Collaborator.objects.create(main_account=self.user, user=admin_user, role=Collaborator.Roles.ADMIN)

        editor_user = get_user_model().objects.create_user(
            username="editor-col",
            email="editor-col@example.com",
            password="Secret123!",
            account_type="collaborator",
        )
        editor_collab = Collaborator.objects.create(
            main_account=self.user, user=editor_user, role=Collaborator.Roles.EDITOR
        )

        # 4. L'éditeur (Collaborateur) NE PEUT PAS inviter ni modifier les rôles
        self.client.force_authenticate(user=editor_user)
        self.assertEqual(
            self.client.patch(
                f"/account/collaborators/{editor_collab.id}/role/",
                {"role": "admin"},
                format="json",
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                "/account/collaborators/",
                {"email": "forbidden@example.com"},
                format="json",
            ).status_code,
            403,
        )
        me_editor = self.client.get("/account/me/")
        self.assertEqual(me_editor.status_code, 200)
        self.assertEqual(me_editor.data["role"], "editor")
        self.assertFalse(me_editor.data["can_manage_collaborators"])
        self.assertTrue(me_editor.data["can_edit"])

        # 5. L'admin collaborateur PEUT rétrograder un collaborateur en viewer (Lecteur) et inviter
        self.client.force_authenticate(user=admin_user)
        patch_role = self.client.patch(
            f"/account/collaborators/{editor_collab.id}/role/",
            {"role": "viewer"},
            format="json",
        )
        self.assertEqual(patch_role.status_code, 200)
        self.assertEqual(patch_role.data["role"], "viewer")

        editor_user.refresh_from_db()
        self.client.force_authenticate(user=editor_user)
        me_viewer = self.client.get("/account/me/")
        self.assertEqual(me_viewer.data["role"], "viewer")
        self.assertFalse(me_viewer.data["can_edit"])
        self.assertFalse(me_viewer.data["can_manage_collaborators"])
