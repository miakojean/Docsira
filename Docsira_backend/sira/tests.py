from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Client.models import Client as ClientModel
from account.models import CustomUser
from affairs.models import Affair
from sira.models import SiraFolderHistory


class SiraHistoryApiTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="sira-owner", password="test-password")
        self.client_record = ClientModel.objects.create(
            type_client="PERSONNE_PHYSIQUE",
            nom="Diallo",
            prenoms="Moussa",
            telephone_1="0700000001",
            charge_de_clientele=self.user,
        )
        self.affair = Affair.objects.create(
            title="Dossier SIRA",
            type_affair="AUTRE",
            firm=self.user,
            client=self.client_record,
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("sira-affair-history", kwargs={"affair_id": self.affair.pk})

    def test_sira_history_filters_and_firm_isolation(self):
        SiraFolderHistory.objects.create(
            affair_id=self.affair.pk,
            previous_progression=10,
            new_progression=45,
            action_type="AJOUT_DOCUMENT",
            document_title="CNI.pdf",
            category="IDENTIFICATION",
            author="sira-owner",
            details="Ajout initial",
        )
        SiraFolderHistory.objects.create(
            affair_id=self.affair.pk,
            previous_progression=45,
            new_progression=45,
            action_type="NOUVELLE_VERSION",
            document_title="CNI.pdf",
            category="IDENTIFICATION",
            author="sira-owner",
            details="v2 ajoutée",
        )

        all_resp = self.client.get(self.url)
        self.assertEqual(all_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(all_resp.data["count"], 2)

        filtered = self.client.get(self.url + "?action_type=NOUVELLE_VERSION")
        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(filtered.data["count"], 1)
        self.assertEqual(filtered.data["results"][0]["action_type"], "NOUVELLE_VERSION")

        other_firm = CustomUser.objects.create_user(username="sira-other", password="test-password")
        self.client.force_authenticate(user=other_firm)
        denied = self.client.get(self.url)
        self.assertEqual(denied.status_code, status.HTTP_404_NOT_FOUND)
