from rest_framework.generics import ListAPIView

from apps.core.models import OrgnameT
from apps.master.serializers.orgname_t_serializers import OrgnameTSerializer


class OrgnameTListView(ListAPIView):
    queryset = OrgnameT.objects.all()
    serializer_class = OrgnameTSerializer
    pagination_class = None  # Disable pagination for this view
