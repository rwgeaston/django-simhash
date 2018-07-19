from rest_framework import viewsets

from .models import SimHash
from .calculate_simhash import calculate_simhash
from .serializers import SimHashSerializer


class HashViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors

    queryset = SimHash.objects.all()
    serializer_class = SimHashSerializer

    def create(self, request, *args, **kwargs):
        calculate_simhash(request.data)
        return super().create(request, *args, **kwargs)
