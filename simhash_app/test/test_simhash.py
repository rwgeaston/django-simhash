# pylint: skip-file
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class SimhashTest(TestCase):

    def setUp(self):
        self.maxDiff = None

        self.user = User.objects.create(email='testuser@rwgeaston.com')
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.key))

    def test_get_hashes_list(self):
        response = self.client.get('/hashes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'count': 0, 'next': None, 'previous': None, 'results': []})
