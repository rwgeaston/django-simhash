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


# Although this mixin is extremely interconnected with the SimHash model,
# it was just too much code to dump in the models file
class SimHashSaveMixin():
    # If we are saving this because we found it's a near duplicate while saving something else
    # then we don't want to get into an infinite loop of saving the same two over and over
    needs_related_check = True

    # Dict or list of SimHashes which need to be re-saved because this one is being resaved
    related_needs_save = tuple()

    permutations_model = models.Model

    # Permutations which need to be saved after saving this Simhash
    new_permutations = tuple()

    def post_save_related_models_save(self):
        for permutation in self.new_permutations:
            permutation.sim_hash = self
            permutation.save()

        for sim_hash in self.related_needs_save.values():
            if sim_hash:
                sim_hash.nearest_duplicate = self
                sim_hash.save()

    def generate_permutations(self):
        self.permutations.all().delete()
        permutations = []
        hash_permutation = self.hash
        closest_match = None
        bits_differ = hash_length + 1

        perfect_match = (
            self.__class__.objects
            .filter(source=self.source)
            .filter(method=self.method)
            .filter(hash=self.hash)
            .exclude(guid=self.guid)
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

            permutations.append(self.permutations_model(
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
            self.permutations_model.objects
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
            self.permutations_model.objects
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
