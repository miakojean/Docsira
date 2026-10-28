import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from Client.models import Client as ClientModel
from account.models import CustomUser
from .models import Affair, Document


class AffairDocumentsApiTests(APITestCase):
	def setUp(self):
		self.media_directory = tempfile.TemporaryDirectory()
		media_settings = override_settings(MEDIA_ROOT=self.media_directory.name)
		media_settings.enable()
		self.addCleanup(media_settings.disable)
		self.addCleanup(self.media_directory.cleanup)

		self.user = CustomUser.objects.create_user(username="firm-owner", password="test-password")
		self.client_record = ClientModel.objects.create(
			type_client="PERSONNE_PHYSIQUE",
			nom="Doe",
			prenoms="Jane",
			telephone_1="0700000000",
			charge_de_clientele=self.user,
		)
		self.affair = Affair.objects.create(
			title="Dossier de test",
			type_affair="AUTRE",
			firm=self.user,
			client=self.client_record,
		)
		self.client.force_authenticate(user=self.user)
		self.url = reverse("affair-documents", kwargs={"affair_id": self.affair.pk})

	def test_upload_multiple_files_and_list_them(self):
		response = self.client.post(
			self.url,
			{
				"files": [
					SimpleUploadedFile("contrat.pdf", b"pdf content", content_type="application/pdf"),
					SimpleUploadedFile("annexe.txt", b"text content", content_type="text/plain"),
				]
			},
			format="multipart",
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(len(response.data), 2)
		self.assertEqual(Document.objects.filter(affair=self.affair).count(), 2)
		first = Document.objects.get(affair=self.affair, relation=Document.Relation.INITIAL)
		second = Document.objects.get(affair=self.affair, relation=Document.Relation.ADDED)
		self.assertIsNone(first.parent)
		self.assertEqual(second.parent_id, first.id)
		self.affair.refresh_from_db()
		self.assertEqual(self.affair.statut, "EN_COURS")

		list_response = self.client.get(self.url)
		self.assertEqual(list_response.status_code, 200)
		self.assertEqual(len(list_response.data), 2)
		self.assertEqual({item["file_name"] for item in list_response.data}, {"contrat.pdf", "annexe.txt"})

	def test_upload_requires_at_least_one_file(self):
		response = self.client.post(self.url, {}, format="multipart")

		self.assertEqual(response.status_code, 400)
		self.assertIn("files", response.data)

	def test_other_firm_cannot_list_or_upload_documents(self):
		other_user = CustomUser.objects.create_user(username="other-firm", password="test-password")
		self.client.force_authenticate(user=other_user)

		list_response = self.client.get(self.url)
		upload_response = self.client.post(
			self.url,
			{"files": [SimpleUploadedFile("secret.pdf", b"secret")]},
			format="multipart",
		)

		self.assertEqual(list_response.status_code, 403)
		self.assertEqual(upload_response.status_code, 403)
		self.assertFalse(Document.objects.filter(affair=self.affair).exists())
