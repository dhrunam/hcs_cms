from rest_framework import permissions
from rest_framework.generics import ListAPIView

from apps.core.models import District
from apps.master.serializers.district_serializers import DistrictSerializer


class DistrictListView(ListAPIView):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
