from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.models import EfilingLitigant
from apps.efiling.serializers.efiling_litigant_serializers import EfilingLitigantSerializer


class EfilingLitigantListCreateView(ListCreateAPIView):
    queryset = EfilingLitigant.objects.all()
    serializer_class = EfilingLitigantSerializer

    def get_queryset(self):
        qs = EfilingLitigant.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        efiling_id = self.request.query_params.get('efiling_id')
        if efiling_id is not None:
            qs = qs.filter(efiling=efiling_id)
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class EfilingLitigantRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = EfilingLitigant.objects.all()
    serializer_class = EfilingLitigantSerializer

    def get_queryset(self):
        qs = EfilingLitigant.objects.all().order_by('-id')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            # treat "true"/"1" as True
            qs = qs.filter(is_active=is_active.lower() in ['true', '1'])
        return qs   