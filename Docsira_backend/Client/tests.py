from django.urls import reverse
from rest_framework.test import APITestCase


from account.models import CustomUser
from .models import Client


class ClientArchiveApiTests(APITestCase):
	def setUp(self):
		self.user = CustomUser.objects.create_user(username="client-owner", password="test-password")
		self.client_record = Client.objects.create(
			type_client="PERSONNE_PHYSIQUE",
			nom="Doe",
			prenoms="Jane",
			telephone_1="0700000000",
			charge_de_clientele=self.user,
		)
		self.client.force_authenticate(user=self.user)

	def test_archive_list_and_restore_client(self):
		archive_url = reverse("client-archive", kwargs={"client_id": self.client_record.pk})

		archive_response = self.client.post(archive_url)
		self.assertEqual(archive_response.status_code, 200)
		self.client_record.refresh_from_db()
		self.assertEqual(self.client_record.statut, "ARCHIVE")

		archived_response = self.client.get(reverse("client-archives"))
		self.assertEqual(archived_response.status_code, 200)
		self.assertEqual(
			[item["id"] for item in archived_response.data["results"]],
			[str(self.client_record.pk)],
		)

		active_response = self.client.get(reverse("client"))
		self.assertEqual(active_response.status_code, 200)
		self.assertEqual(active_response.data["results"], [])

		restore_response = self.client.delete(archive_url)
		self.assertEqual(restore_response.status_code, 200)
		self.client_record.refresh_from_db()
		self.assertEqual(self.client_record.statut, "ACTIF")
