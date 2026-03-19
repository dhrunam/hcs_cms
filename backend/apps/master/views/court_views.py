from rest_framework import permissions
from rest_framework.generics import ListAPIView

from apps.core.models import Court
from apps.master.serializers.court_serializers import CourtSerializer


class CourtListView(ListAPIView):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
