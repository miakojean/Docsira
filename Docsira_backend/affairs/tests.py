import io
import tempfile
import os
import zipfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from Client.models import Client as ClientModel
from account.models import Collaborator, CustomUser
from .models import Affair, AffairComment, Document


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
					SimpleUploadedFile(
						"annexe.docx",
						b"docx content",
						content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
					),
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
		expected_directory = os.path.relpath(self.affair.path_affair, settings.MEDIA_ROOT).replace("\\", "/")
		self.assertEqual(os.path.dirname(first.file.name), expected_directory)
		self.assertEqual(os.path.dirname(second.file.name), expected_directory)
		self.affair.refresh_from_db()
		self.assertEqual(self.affair.statut, "EN_COURS")

		list_response = self.client.get(self.url)
		self.assertEqual(list_response.status_code, 200)
		self.assertEqual(list_response.data["count"], 2)
		self.assertEqual(len(list_response.data["results"]), 2)
		self.assertEqual({item["file_name"] for item in list_response.data["results"]}, {"contrat.pdf", "annexe.docx"})

	def test_affair_documents_pagination(self):
		upload_resp = self.client.post(
			self.url,
			{
				"files": [
					SimpleUploadedFile("doc1.pdf", b"%PDF-1.4 1", content_type="application/pdf"),
					SimpleUploadedFile("doc2.pdf", b"%PDF-1.4 2", content_type="application/pdf"),
					SimpleUploadedFile("doc3.pdf", b"%PDF-1.4 3", content_type="application/pdf"),
				]
			},
			format="multipart",
		)
		self.assertEqual(upload_resp.status_code, 201)

		page1 = self.client.get(self.url + "?page=1&page_size=2")
		self.assertEqual(page1.status_code, 200)
		self.assertEqual(page1.data["count"], 3)
		self.assertEqual(len(page1.data["results"]), 2)
		self.assertIsNotNone(page1.data["next"])

		page2 = self.client.get(self.url + "?page=2&page_size=2")
		self.assertEqual(page2.status_code, 200)
		self.assertEqual(len(page2.data["results"]), 1)
		self.assertIsNone(page2.data["next"])

	def test_reject_disallowed_document_formats_and_allow_images(self):
		for filename, content_type in [
			("notes.txt", "text/plain"),
			("tableau.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
		]:
			response = self.client.post(
				self.url,
				{"files": [SimpleUploadedFile(filename, b"dummy", content_type=content_type)]},
				format="multipart",
			)
			self.assertEqual(response.status_code, 400)
			self.assertIn("files", response.data)
			self.assertIn("error", response.data)

		self.assertEqual(Document.objects.filter(affair=self.affair).count(), 0)

		img_response = self.client.post(
			self.url,
			{"files": [SimpleUploadedFile("piece_identite.png", b"\x89PNG\r\n\x1a\n", content_type="image/png")]},
			format="multipart",
		)
		self.assertEqual(img_response.status_code, 201)
		self.assertEqual(Document.objects.filter(affair=self.affair).count(), 1)

	def test_download_document_and_firm_isolation(self):
		upload_resp = self.client.post(
			self.url,
			{"files": [SimpleUploadedFile("statuts.pdf", b"%PDF-1.4 content", content_type="application/pdf")]},
			format="multipart",
		)
		self.assertEqual(upload_resp.status_code, 201)
		doc_id = upload_resp.data[0]["id"]
		download_url = reverse("document-download", kwargs={"document_id": doc_id})

		response = self.client.get(download_url)
		self.assertEqual(response.status_code, 200)
		content = b"".join(response.streaming_content)
		response.close()
		self.assertEqual(content, b"%PDF-1.4 content")

		other_user = CustomUser.objects.create_user(username="other-firm-dl", password="test-password")
		self.client.force_authenticate(user=other_user)
		other_resp = self.client.get(download_url)
		self.assertEqual(other_resp.status_code, 404)

	def test_upload_new_document_version(self):
		upload_resp = self.client.post(
			self.url,
			{"files": [SimpleUploadedFile("contrat_v1.doc", b"v1 content", content_type="application/msword")]},
			format="multipart",
		)
		self.assertEqual(upload_resp.status_code, 201)
		v1_id = upload_resp.data[0]["id"]
		version_url = reverse("document-versions", kwargs={"document_id": v1_id})

		# Rejeter les formats autres que PDF/Word
		bad_resp = self.client.post(
			version_url,
			{"file": SimpleUploadedFile("bad.txt", b"text", content_type="text/plain")},
			format="multipart",
		)
		self.assertEqual(bad_resp.status_code, 400)

		# Accepter v2 Word/PDF
		v2_resp = self.client.post(
			version_url,
			{"file": SimpleUploadedFile("contrat_v2.docx", b"v2 content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
			format="multipart",
		)
		self.assertEqual(v2_resp.status_code, 201)
		self.assertEqual(v2_resp.data["version"], 2)
		self.assertEqual(v2_resp.data["relation"], Document.Relation.UPDATED)
		self.assertEqual(str(v2_resp.data["parent"]), str(v1_id))

		other_user = CustomUser.objects.create_user(username="other-firm-ver", password="test-password")
		self.client.force_authenticate(user=other_user)
		other_resp = self.client.post(
			version_url,
			{"file": SimpleUploadedFile("hack.pdf", b"hack", content_type="application/pdf")},
			format="multipart",
		)
		self.assertEqual(other_resp.status_code, 404)

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

	def test_archive_list_and_restore_affair(self):
		archive_url = reverse("affair-archive", kwargs={"affair_id": self.affair.pk})
		archive_list_url = reverse("affair-archives")

		archive_response = self.client.post(archive_url)
		self.assertEqual(archive_response.status_code, 200)
		self.affair.refresh_from_db()
		self.assertTrue(self.affair.is_archived)

		archived_response = self.client.get(archive_list_url)
		self.assertEqual(archived_response.status_code, 200)
		self.assertEqual([item["id"] for item in archived_response.data["results"]], [str(self.affair.pk)])

		active_response = self.client.get(reverse("affair-list"))
		self.assertEqual(active_response.status_code, 200)
		self.assertEqual(active_response.data["results"], [])

		restore_response = self.client.delete(archive_url)
		self.assertEqual(restore_response.status_code, 200)
		self.affair.refresh_from_db()
		self.assertFalse(self.affair.is_archived)

	def test_rename_and_move_document_to_another_affair(self):
		upload_resp = self.client.post(
			self.url,
			{"files": [SimpleUploadedFile("piece.pdf", b"%PDF-1.4 data", content_type="application/pdf")]},
			format="multipart",
		)
		self.assertEqual(upload_resp.status_code, 201)
		doc_id = upload_resp.data[0]["id"]
		doc_url = reverse("document-id", kwargs={"document_id": doc_id})

		# 1. Renommer
		rename_resp = self.client.patch(doc_url, {"title": "Statuts signés"}, format="json")
		self.assertEqual(rename_resp.status_code, 200)
		self.assertEqual(rename_resp.data["title"], "Statuts signés")

		# 2. Déplacer vers un autre dossier du même cabinet
		other_affair = Affair.objects.create(
			title="Dossier cible",
			type_affair="AUTRE",
			firm=self.user,
			client=self.client_record,
		)
		move_resp = self.client.patch(doc_url, {"affair": str(other_affair.pk)}, format="json")
		self.assertEqual(move_resp.status_code, 200)
		self.assertEqual(str(move_resp.data["affair"]), str(other_affair.pk))
		self.assertEqual(Document.objects.filter(affair=self.affair).count(), 0)
		self.assertEqual(Document.objects.filter(affair=other_affair).count(), 1)

	def test_create_public_access_and_revoke_share_link(self):
		upload_resp = self.client.post(
			self.url,
			{"files": [SimpleUploadedFile("rapport.pdf", b"%PDF-1.4 shared", content_type="application/pdf")]},
			format="multipart",
		)
		self.assertEqual(upload_resp.status_code, 201)
		doc_id = upload_resp.data[0]["id"]
		links_url = reverse("document-share-links", kwargs={"document_id": doc_id})

		# Création du lien
		create_resp = self.client.post(links_url, {"expires_in_days": 7}, format="json")
		self.assertEqual(create_resp.status_code, 201)
		token = create_resp.data["token"]
		link_id = create_resp.data["id"]
		self.assertIn(f"/affairs/share/{token}/", create_resp.data["share_url"])

		# Accès public sans authentification
		public_url = reverse("public-document-share", kwargs={"token": token})
		self.client.force_authenticate(user=None)
		public_resp = self.client.get(public_url)
		self.assertEqual(public_resp.status_code, 200)
		content = b"".join(public_resp.streaming_content)
		public_resp.close()
		self.assertEqual(content, b"%PDF-1.4 shared")

		# Vérifier l'incrément download_count et révoquer
		self.client.force_authenticate(user=self.user)
		list_resp = self.client.get(links_url)
		self.assertEqual(list_resp.status_code, 200)
		self.assertEqual(list_resp.data[0]["download_count"], 1)

		revoke_url = reverse(
			"document-share-link-detail",
			kwargs={"document_id": doc_id, "link_id": link_id},
		)
		revoke_resp = self.client.delete(revoke_url)
		self.assertEqual(revoke_resp.status_code, 204)

		self.client.force_authenticate(user=None)
		after_revoke = self.client.get(public_url)
		self.assertEqual(after_revoke.status_code, 404)

	def test_create_public_zip_access_and_revoke_affair_share_link(self):
		upload_resp = self.client.post(
			self.url,
			{"files": [SimpleUploadedFile("statuts_dossier.pdf", b"%PDF-1.4 dossier", content_type="application/pdf")]},
			format="multipart",
		)
		self.assertEqual(upload_resp.status_code, 201)

		links_url = reverse("affair-share-links", kwargs={"affair_id": self.affair.pk})
		create_resp = self.client.post(links_url, {"expires_in_days": 7}, format="json")
		self.assertEqual(create_resp.status_code, 201)
		token = create_resp.data["token"]
		link_id = create_resp.data["id"]
		self.assertIn(f"/affairs/share/dossier/{token}/", create_resp.data["share_url"])

		# Accès public ZIP sans authentification
		public_url = reverse("public-affair-share", kwargs={"token": token})
		self.client.force_authenticate(user=None)
		public_resp = self.client.get(public_url)
		self.assertEqual(public_resp.status_code, 200)
		zip_bytes = b"".join(public_resp.streaming_content)
		public_resp.close()

		with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
			names = zf.namelist()
			self.assertEqual(len(names), 1)
			self.assertTrue(names[0].endswith(".pdf"))
			self.assertEqual(zf.read(names[0]), b"%PDF-1.4 dossier")

		# Vérifier compteur + révocation
		self.client.force_authenticate(user=self.user)
		list_resp = self.client.get(links_url)
		self.assertEqual(list_resp.status_code, 200)
		self.assertEqual(list_resp.data[0]["download_count"], 1)

		revoke_url = reverse(
			"affair-share-link-detail",
			kwargs={"affair_id": self.affair.pk, "link_id": link_id},
		)
		self.assertEqual(self.client.delete(revoke_url).status_code, 204)

		self.client.force_authenticate(user=None)
		self.assertEqual(self.client.get(public_url).status_code, 404)

	def test_trash_restore_and_permanent_delete_for_affairs_and_documents(self):
		upload_resp = self.client.post(
			self.url,
			{"files": [SimpleUploadedFile("piece_trash.pdf", b"%PDF-1.4 trash", content_type="application/pdf")]},
			format="multipart",
		)
		self.assertEqual(upload_resp.status_code, 201)
		doc_id = upload_resp.data[0]["id"]

		# 1. Soft-delete document -> va dans la corbeille
		doc_url = reverse("document-id", kwargs={"document_id": doc_id})
		del_doc_resp = self.client.delete(doc_url)
		self.assertEqual(del_doc_resp.status_code, 200)
		self.assertEqual(self.client.get(self.url).data["results"], [])

		trash_docs_resp = self.client.get(reverse("document-list") + "?trash=true")
		self.assertEqual(trash_docs_resp.status_code, 200)
		self.assertEqual([d["id"] for d in trash_docs_resp.data["results"]], [str(doc_id)])

		# 2. Restaurer le document
		restore_doc_url = reverse("document-restore", kwargs={"document_id": doc_id})
		self.assertEqual(self.client.post(restore_doc_url).status_code, 200)
		self.assertEqual(len(self.client.get(self.url).data["results"]), 1)

		# 3. Suppression définitive du document
		perm_doc_url = reverse("document-permanent-delete", kwargs={"document_id": doc_id})
		self.assertEqual(self.client.delete(perm_doc_url).status_code, 200)
		self.assertFalse(Document.objects.filter(pk=doc_id).exists())

		# 4. Soft-delete dossier -> va dans la corbeille
		affair_detail_url = reverse("affair-detail", kwargs={"affair_id": self.affair.pk})
		self.assertEqual(self.client.delete(affair_detail_url).status_code, 200)
		self.assertEqual(self.client.get(reverse("affair-list")).data["results"], [])

		trash_affairs_resp = self.client.get(reverse("affair-list") + "?trash=true")
		self.assertEqual(trash_affairs_resp.status_code, 200)
		self.assertEqual([a["id"] for a in trash_affairs_resp.data["results"]], [str(self.affair.pk)])

		# 5. Restaurer le dossier
		restore_affair_url = reverse("affair-restore", kwargs={"affair_id": self.affair.pk})
		self.assertEqual(self.client.post(restore_affair_url).status_code, 200)
		self.assertEqual(len(self.client.get(reverse("affair-list")).data["results"]), 1)

		# 6. Suppression définitive du dossier
		perm_affair_url = reverse("affair-permanent-delete", kwargs={"affair_id": self.affair.pk})
		self.assertEqual(self.client.delete(perm_affair_url).status_code, 200)
		self.assertFalse(Affair.objects.filter(pk=self.affair.pk).exists())

	def test_affair_comments_crud_replies_and_permissions(self):
		upload_resp = self.client.post(
			self.url,
			{"files": [SimpleUploadedFile("note.pdf", b"%PDF-1.4 note", content_type="application/pdf")]},
			format="multipart",
		)
		self.assertEqual(upload_resp.status_code, 201)
		doc_id = upload_resp.data[0]["id"]

		comments_url = reverse("affair-comments", kwargs={"affair_id": self.affair.pk})

		# 1. Commentaire général par le propriétaire
		create_root = self.client.post(
			comments_url,
			{"content": "Merci de vérifier les statuts avant signature."},
			format="json",
		)
		self.assertEqual(create_root.status_code, 201)
		root_id = create_root.data["id"]
		self.assertTrue(create_root.data["can_edit"])
		self.assertTrue(create_root.data["can_delete"])

		# 2. Réponse par un collaborateur (éditeur) liée à un document
		collab_user = CustomUser.objects.create_user(
			username="collab-comment",
			first_name="Awa",
			last_name="Kone",
			password="test-password",
			account_type=CustomUser.AccountType.COLLABORATOR,
		)
		Collaborator.objects.create(main_account=self.user, user=collab_user, role=Collaborator.Roles.EDITOR)

		self.client.force_authenticate(user=collab_user)
		reply_resp = self.client.post(
			comments_url,
			{
				"content": "Relu et validé pour l'annexe.",
				"document": doc_id,
				"parent": root_id,
			},
			format="json",
		)
		self.assertEqual(reply_resp.status_code, 201)
		reply_id = reply_resp.data["id"]
		self.assertEqual(str(reply_resp.data["parent"]), str(root_id))
		self.assertEqual(reply_resp.data["author_name"], "Awa Kone")
		self.assertEqual(reply_resp.data["author_initials"], "AK")

		# 3. Liste chronologique + filtre par document
		list_resp = self.client.get(comments_url)
		self.assertEqual(list_resp.status_code, 200)
		self.assertEqual(len(list_resp.data), 2)

		filtered_resp = self.client.get(comments_url + f"?document={doc_id}")
		self.assertEqual(filtered_resp.status_code, 200)
		self.assertEqual([c["id"] for c in filtered_resp.data], [reply_id])

		# 4. Le collaborateur ne peut pas modifier/supprimer le commentaire du propriétaire
		root_detail_url = reverse("affair-comment-detail", kwargs={"comment_id": root_id})
		self.assertEqual(self.client.patch(root_detail_url, {"content": "Piraté"}, format="json").status_code, 403)
		self.assertEqual(self.client.delete(root_detail_url).status_code, 403)

		# 5. Le collaborateur peut modifier son propre commentaire
		reply_detail_url = reverse("affair-comment-detail", kwargs={"comment_id": reply_id})
		edit_resp = self.client.patch(reply_detail_url, {"content": "Relu et corrigé."}, format="json")
		self.assertEqual(edit_resp.status_code, 200)
		self.assertTrue(edit_resp.data["is_edited"])
		self.assertEqual(edit_resp.data["content"], "Relu et corrigé.")

		# 6. Isolation autre cabinet -> 404
		other_firm = CustomUser.objects.create_user(username="other-firm-comments", password="test-password")
		self.client.force_authenticate(user=other_firm)
		self.assertEqual(self.client.get(comments_url).status_code, 404)
		self.assertEqual(self.client.delete(root_detail_url).status_code, 404)

		# 7. Le propriétaire du cabinet peut supprimer n'importe quel commentaire du dossier
		self.client.force_authenticate(user=self.user)
		self.assertEqual(self.client.delete(reply_detail_url).status_code, 200)
		self.assertFalse(AffairComment.objects.filter(pk=reply_id).exists())
