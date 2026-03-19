from rest_framework.generics import ListAPIView

from apps.core.models import Court
from apps.master.serializers.court_serializers import CourtSerializer


class CourtListView(ListAPIView):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
