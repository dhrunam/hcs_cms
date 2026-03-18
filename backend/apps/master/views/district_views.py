from rest_framework.generics import ListAPIView

from apps.core.models import District
from apps.master.serializers.district_serializers import DistrictSerializer


class DistrictListView(ListAPIView):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    
    def get_queryset(self):
        #filter districts based on state_id query parameter
        queryset = super().get_queryset()
        state_id = self.request.query_params.get('state_id')
        if state_id is not None:
            queryset = queryset.filter(state_id=state_id)
        return queryset
