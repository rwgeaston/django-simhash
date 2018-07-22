from django.db import models

from simhash import hamming_distance
from .calculate_simhash import hash_length
from .calculate_simhash import highest_value


def rotate_bits(num):
    response = (num >> 1)
    if num > 0 and num % 2 == 1:
        response -= highest_value
    elif num < 0 and num % 2 == 0:
        response += highest_value
    return response


class SimHash(models.Model):
    # Short free text for params of simhash generation.
    method = models.CharField(max_length=30)

    # Other system can look up what it sent by this guid. Where this text came from is their problem.
    guid = models.CharField(max_length=36)
    source = models.CharField(max_length=30)  # We only compare to texts with same source

    nearest_duplicate = models.ForeignKey(
        "self", blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='nearest_reverse'
    )
    bits_differ = models.IntegerField(blank=True, null=True)  # compared to above duplicate
    hash = models.BigIntegerField()

    # If we are saving this because we found it's a near duplicate while saving something else
    # then we don't want to get into an infinite loop of saving the same two over and over
    needs_related_check = True

    # Dict or list of SimHashes which need to be re-saved because this one is being resaved
    related_needs_save = tuple()

    class Meta:
        unique_together = (
            ('guid', 'source', 'method'),
        )

    def save(self, **kwargs):  # pylint: disable=arguments-differ
        new_permutations = []
        self.related_needs_save = {}
        if self.needs_related_check:
            new_permutations = self.generate_permutations()

        response = super().save(**kwargs)

        for permutation in new_permutations:
            permutation.sim_hash = self
            permutation.save()

        for sim_hash in self.related_needs_save.values():
            if sim_hash:
                sim_hash.nearest_duplicate = self
                sim_hash.save()

        return response

    def generate_permutations(self):
        self.permutations.all().delete()
        permutations = []
        hash_permutation = self.hash
        closest_match = None
        bits_differ = hash_length + 1

        perfect_match = (
            SimHash.objects
            .filter(source=self.source)
            .filter(method=self.method)
            .filter(hash=self.hash - highest_value)
        )

        if self.pk:
            perfect_match.exclude(pk=self.pk)

        perfect_match = perfect_match.first()

        if perfect_match:
            closest_match = perfect_match
            bits_differ = 0

        for permutation_num in range(hash_length):
            closest_match, bits_differ = self.find_closest_permutation(
                closest_match, bits_differ,
                permutation_num, hash_permutation,
            )

            permutations.append(Permutation(
                bits_rotated=permutation_num,
                hash=hash_permutation,
                sim_hash=self
            ))
            hash_permutation = rotate_bits(hash_permutation)

        assert hash_permutation == self.hash
        self.nearest_duplicate = closest_match
        self.bits_differ = bits_differ

        return permutations

    def find_closest_permutation(self, closest_match, bits_differ, permutation_num, hash_permutation):
        closest_above = (
            Permutation.objects
            .filter(sim_hash__source=self.source)
            .filter(sim_hash__method=self.method)
            .filter(bits_rotated=permutation_num)
            .filter(hash__gt=hash_permutation)
            .order_by('hash')
            .first()
        )

        if closest_above:
            distance = hamming_distance(hash_permutation, closest_above.hash)
            if distance < bits_differ:
                closest_match, bits_differ = closest_above.sim_hash, distance

            self.check_nearest_reverse(closest_above, distance)

        closest_below = (
            Permutation.objects
            .filter(sim_hash__source=self.source)
            .filter(sim_hash__method=self.method)
            .filter(bits_rotated=permutation_num)
            .filter(hash__lt=hash_permutation)
            .order_by('-hash')
            .first()
        )

        if closest_below:
            distance = hamming_distance(hash_permutation, closest_below.hash)
            if distance < bits_differ:
                closest_match, bits_differ = closest_below.sim_hash, distance

            self.check_nearest_reverse(closest_below, distance)

        return closest_match, bits_differ

    def check_nearest_reverse(self, related_permutation, distance):
        related_simhash = related_permutation.sim_hash
        if related_simhash.id in self.related_needs_save:
            return

        if distance < related_simhash.bits_differ:
            related_simhash.bits_differ = distance
            self.related_needs_save[related_simhash.id] = related_simhash
            related_simhash.needs_related_check = False
        else:
            self.related_needs_save[related_simhash.id] = False


    def __str__(self):
        return self.guid


class Permutation(models.Model):
    sim_hash = models.ForeignKey(SimHash, on_delete=models.CASCADE, related_name='permutations')
    hash = models.BigIntegerField()
    bits_rotated = models.IntegerField()
