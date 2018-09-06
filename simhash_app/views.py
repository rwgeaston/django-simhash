from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from .models import SimHash
from .calculate_simhash import calculate_simhash
from .serializers import SimHashSerializer


class HashViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors

    queryset = SimHash.objects.all()
    serializer_class = SimHashSerializer
    lookup_field = 'guid'

    def create(self, request, *args, **kwargs):
        calculate_simhash(request.data)
        return super().create(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def get_nearest(self, request):
        params = dict(request.GET.items())
        calculate_simhash(params)
        params.pop('text')
        simhash = SimHash(**params)
        simhash.generate_permutations()
        response = self.serializer_class(simhash).data

        # This is always empty because no nearest entities have been saved
        response.pop('nearest_reverse')

        return JsonResponse(response)
