from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import Organisation

User = get_user_model()


class OrganisationAccessTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            firstName='John',
            lastName='Doe',
            password='testpassword'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            firstName='Jane',
            lastName='Doe',
            password='testpassword'
        )
        self.organisation1 = Organisation.objects.create(name="Org 1")
        self.organisation1.users.add(self.user1)
        self.organisation2 = Organisation.objects.create(name="Org 2")
        self.organisation2.users.add(self.user2)
        self.client.force_authenticate(user=self.user1)

    def test_user_cannot_access_other_organisation(self):
        response = self.client.get(
            f'/api/organisations/{self.organisation2.orgId}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
