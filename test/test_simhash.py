from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

class SimhashTest(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

    def test_get_hashes_list(self):
        response = self.client.get('/hashes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'count': 0, 'next': None, 'previous': None, 'results': []})
