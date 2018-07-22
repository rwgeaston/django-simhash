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
        response = self.client.get('/hashes/1234/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['nearest_duplicate'], '1235')
        self.assertEqual(response.json()['nearest_reverse'], ['1235'])

    def test_delete_hash(self):
        self.client.post(
            '/hashes/', format='json',
            data={
                'guid': '1234', 'source': 'test',
                'text': 'this string has some things in common second half nonsense gibberish',
            }
        )

        response = self.client.post(
            '/hashes/', format='json',
            data={
                'guid': '1236', 'source': 'test',
                'text': 'first bit rubbish chaos common with both other strings',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['nearest_duplicate'], '1234')
        original_bits_differ = response.json()['bits_differ']

        response = self.client.get('/hashes/1234/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['nearest_duplicate'], '1236')

        # So far we have two quite dissimilar texts so it's easy to stick one in-between them
        response = self.client.post(
            '/hashes/', format='json',
            data={
                'guid': '1235', 'source': 'test',
                'text': 'this string has some things in common with both other strings',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['bits_differ'], 18)
        self.assertEqual(
            sorted(response.json()['nearest_reverse']),
            ['1234', '1236'],
        )

        response = self.client.delete('/hashes/1235/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Having deleted 1235, we should now find 1234 and 1236 are nearest duplicates of each other again
        response = self.client.get('/hashes/')
        hashes = response.json()['results']
        hashes.sort(key=lambda hash: hash['guid'])

        self.assertEqual(hashes[0]['guid'], '1234')
        self.assertEqual(hashes[0]['nearest_duplicate'], '1236')
        self.assertEqual(hashes[0]['nearest_reverse'], ['1236'])
        self.assertEqual(hashes[0]['bits_differ'], original_bits_differ)

        self.assertEqual(hashes[1]['guid'], '1236')
        self.assertEqual(hashes[1]['nearest_duplicate'], '1234')
        self.assertEqual(hashes[1]['nearest_reverse'], ['1234'])
        self.assertEqual(hashes[1]['bits_differ'], original_bits_differ)
