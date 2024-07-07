from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
import jwt
from django.conf import settings
import os
from dotenv import load_dotenv
from pathlib import Path

User = get_user_model()
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))


class TokenGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            firstName='John',
            lastName='Doe',
            password='testpassword',
            phone='1234567890'
        )

    def test_token_contains_user_details(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        decoded_payload = jwt.decode(
            access_token,
            os.getenv('SIGNING_KEY'),
            algorithms=["HS256"]
        )
        self.assertEqual(decoded_payload['user_id'], str(self.user.userId))


class RegisterEndpointTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user_success(self):
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'test@example.com',
            'password': 'testpassword',
            'phone': '1234567890'
        }
        response = self.client.post('/auth/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']
                         ['user']['email'], 'test@example.com')

    def test_login_user_success(self):
        User.objects.create_user(
            email='test@example.com',
            firstName='John',
            lastName='Doe',
            password='testpassword',
            phone='1234567890'
        )
        data = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        response = self.client.post('/auth/login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']
                         ['user']['email'], 'test@example.com')

    def test_register_missing_fields(self):
        data = {
            'firstName': 'John',
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        response = self.client.post('/auth/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('lastName', response.data)

    def test_register_duplicate_email(self):
        User.objects.create_user(
            email='test@example.com',
            firstName='John',
            lastName='Doe',
            password='testpassword',
            phone='1234567890'
        )
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'test@example.com',
            'password': 'testpassword',
            'phone': '1234567890'
        }
        response = self.client.post('/auth/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
