from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from simhash_app.calculate_simhash import hash_length

class SimhashTest(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.client = APIClient()

    def test_get_hashes_list(self):
        response = self.client.get('/hashes/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'count': 0, 'next': None, 'previous': None, 'results': []})

    def test_post_hashes(self):
        response = self.client.post(
            '/hashes/', format='json',
            data={
                'guid': '1234', 'source': 'test',
                'text': 'this is a moderate length text with enough words we can change to make it similar',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['bits_differ'], hash_length + 1)
        self.assertEqual(response.json()['nearest_duplicate'], None)
