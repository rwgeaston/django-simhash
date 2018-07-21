from hashlib import md5

from rest_framework.exceptions import ValidationError
from simhash import fingerprint

hash_length = 64
highest_value = 1 << (hash_length - 1)
hex_hash_length = hash_length // 4


def calculate_simhash(data):
    text = data['text']
    word_group_length = data.get('word_group_length', 3)

    for punctuation in '.!?,':
        text = text.replace(punctuation, '')

    words = text.split(' ')
    if len(words) < word_group_length:
        raise ValidationError(f"Text is too short for word group length ({word_group_length})")

    data.update(generate_hash(words, word_group_length))


def generate_hash(words, word_group_length):
    hashes = []
    for index in range(len(words) - word_group_length + 1):
        grouping = ' '.join(words[index:index+word_group_length])

        # Some magic shit to get a 64 signed int hash
        # Doesn't really matter how you do it if it's consistent
        # python inbuilt hash is not
        hex_hash = md5(grouping.encode('utf8')).hexdigest()

        int_hash = int(hex_hash[:hex_hash_length], 16) - highest_value
        hashes.append(int_hash)

    simhash = {
        'hash': fingerprint(hashes),
        # Important that we only compare hashes generated the same way
        'method': f'md5_1st_half_{word_group_length}-grams'
    }
    return simhash
