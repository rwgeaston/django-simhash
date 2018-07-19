from django.contrib import admin
from .models import SimHash
from .models import Permutation


@admin.register(SimHash)
class SimHashAdmin(admin.ModelAdmin):
    list_display = (
        'guid',
        'source',
        'method',
        'hash',
        'bits_differ',
    )


@admin.register(Permutation)
class PermutationAdmin(admin.ModelAdmin):
    list_display = (
        'sim_hash',
        'bits_rotated',
        'hash',
    )
