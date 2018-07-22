from django.db import models

from .simhash_save_mixin import SimHashSaveMixin


class SimHash(models.Model, SimHashSaveMixin):
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

    class Meta:
        unique_together = (
            ('guid', 'source', 'method'),
        )

    def save(self, **kwargs):  # pylint: disable=arguments-differ
        self.permutations_model = Permutation
        self.new_permutations = []
        self.related_needs_save = {}
        if self.needs_related_check:
            self.new_permutations = self.generate_permutations()

        response = super().save(**kwargs)
        self.post_save_related_models_save()

        return response

    def __str__(self):
        return self.guid


class Permutation(models.Model):
    sim_hash = models.ForeignKey(SimHash, on_delete=models.CASCADE, related_name='permutations')
    hash = models.BigIntegerField()
    bits_rotated = models.IntegerField()
