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

        response = self.client.post(
            '/hashes/', format='json',
            data={
                'guid': '1235', 'source': 'test',
                'text': 'this is a moderate length text with enough words we can change to make it different',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['bits_differ'], 3)
        self.assertEqual(response.json()['nearest_duplicate'], '1234')

        response = self.client.post(
            '/hashes/', format='json',
            data={
                'guid': '1236', 'source': 'test',
                'text': 'this is a very different set of letters and phrases which barely overlaps at all',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['bits_differ'], 29)
        self.assertEqual(response.json()['nearest_duplicate'], '1235')

        response = self.client.post(
            '/hashes/', format='json',
            data={
                'guid': '1237', 'source': 'test2',
                'text': 'since the source is different, this should not be compared to existing texts at all',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['bits_differ'], hash_length + 1)
        self.assertEqual(response.json()['nearest_duplicate'], None)

        response = self.client.post(
            '/hashes/', format='json',
            data={
                'guid': '1238', 'source': 'test2',
                'text': 'since we are using source test2 again, this should be compared to the previous text',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['bits_differ'], 24)
        self.assertEqual(response.json()['nearest_duplicate'], '1237')

        # This one had no nearest duplicate to start with
        response = self.client.get(
            '/hashes/1234/', format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['nearest_duplicate'], '1235')
        self.assertEqual(response.json()['nearest_reverse'], ['1235'])
