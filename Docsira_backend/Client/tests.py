from django.urls import reverse
from rest_framework.test import APITestCase

from account.models import Collaborator, CustomUser
from affairs.models import Affair
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

	def test_get_single_client_detail_and_firm_isolation(self):
		detail_url = reverse("client_detail", kwargs={"client_id": self.client_record.pk})
		response = self.client.get(detail_url)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(str(response.data["id"]), str(self.client_record.pk))

		other_user = CustomUser.objects.create_user(username="other-firm-client", password="test-password")
		self.client.force_authenticate(user=other_user)
		other_response = self.client.get(detail_url)
		self.assertEqual(other_response.status_code, 404)

	def test_partial_patch_client_without_identity_fields(self):
		detail_url = reverse("client_detail", kwargs={"client_id": self.client_record.pk})
		response = self.client.patch(detail_url, {"ville": "Abidjan"}, format="json")
		self.assertEqual(response.status_code, 200)
		self.client_record.refresh_from_db()
		self.assertEqual(self.client_record.ville, "Abidjan")

	def test_permanent_delete_collaborator_client_and_protected_conflict(self):
		collab_user = CustomUser.objects.create_user(
			username="collab-user",
			email="collab@example.com",
			password="test-password",
			account_type=CustomUser.AccountType.COLLABORATOR,
		)
		Collaborator.objects.create(main_account=self.user, user=collab_user, role=Collaborator.Roles.EDITOR)
		collab_client = Client.objects.create(
			type_client="PERSONNE_PHYSIQUE",
			nom="Kouame",
			prenoms="Paul",
			telephone_1="0701020304",
			charge_de_clientele=collab_user,
			is_deleted=True,
		)

		delete_url = reverse("client_permanent_delete", kwargs={"client_id": collab_client.pk})
		delete_resp = self.client.delete(delete_url)
		self.assertEqual(delete_resp.status_code, 200)
		self.assertFalse(Client.objects.filter(pk=collab_client.pk).exists())

		# Client protégé par une affaire -> 409 Conflict
		Affair.objects.create(
			title="Dossier actif",
			type_affair="AUTRE",
			firm=self.user,
			client=self.client_record,
		)
		protected_url = reverse("client_permanent_delete", kwargs={"client_id": self.client_record.pk})
		protected_resp = self.client.delete(protected_url)
		self.assertEqual(protected_resp.status_code, 409)
