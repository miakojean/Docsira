from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import CustomUserSerializer


class CustomUserSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice",
            email="alice@example.com",
            password="Secret123!",
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
