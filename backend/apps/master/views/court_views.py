from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.models import Court
from apps.master.serializers.court_serializers import CourtSerializer


class CourtListView(ListAPIView):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
